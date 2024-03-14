import os
import pathlib
import shutil
import subprocess
import logging
import psycopg2
import psycopg2.errors
import glob

from collections import namedtuple
from psycopg2 import OperationalError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PATCHES = "patches"
PARENT_PATH = pathlib.Path(__file__).parent.resolve()


def password_for_user(user, prefix):
    """ Retrieves the password to be used in database access. The password is retrieved from
    the environment variable {prefix}{user.upper()}_PASSWORD. If there is no such
    environment variable, the username is used instead.

    :param user: The username
    :param prefix: The prefix used in the environment variable.
    :return: The password stored in the matching environment variable.
    """
    user_upper = user.upper()
    password_key = f'{prefix}{user_upper}_PASSWORD'
    logging.debug(f"Password environment variable={password_key}")
    if password_key in os.environ:
        logging.debug(f'Found database password environment variable for user {user}')
        return os.environ[password_key]
    else:
        logging.warning(f'No database password environment variable for user {user}')
        return user


def database_connection(database_name, user, pwd):
    """ Creates a psycopg2 database connection for the database using username and password. Isolation level is set
    to autocommit.

    :param database_name: The name of the database to connect to.
    :param user: Username to use for the connection
    :param pwd: The password for the user
    :return: A database connection
    :raises: OperationalError: Rethrown from psycopg2.
    """
    try:
        connection = psycopg2.connect(user=user,
                                      password=pwd,
                                      host="127.0.0.1",
                                      port="5432",
                                      database=database_name)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return connection
    except OperationalError as oe:
        logging.debug(f"Caught OperationalError when trying to connect to database {database_name}, rethrowing")
        raise oe


def apply_patches(globs, prefix):
    """ Applies all stored patch files in order. Each patch file is only run once. The files are sorted and applied
    if not applied before. See all_scripts_sorted for sort order.

    :param globs: A list of glob expressions. These expressions are expanded to a set of files.
    :param prefix: The environment variable prefix to be used for database passwords.
    :return: True if successful, otherwise False.
    """
    Patch = namedtuple('Patch', ['database_name', 'major', 'minor', 'user', 'name', 'sql_file'])

    def all_scripts_sorted(paths_list):
        """ Returns a list of Path tuples representing all the sql files in the model catalogs.
        Input file names are encoded. Each part is separated by dot (.).
        First part is the database name.
        Second part is the major version.
        Third part is minor version.
        Fourth part is database username.
        Fifth part is patch name.

        :param paths_list: A list of path names.
        :return: A sorted list of Patch tuples.
        """
        p_list = []
        for path in paths_list:
            path_file = os.path.split(path)
            file_name = path_file[1]
            file_parts = file_name.split(".")
            database_name = file_parts[0]
            major = file_parts[1]
            minor = file_parts[2]
            user = file_parts[3]
            name = file_parts[4]
            p_list.append(Patch(database_name, major, minor, user, name, path))
        return sorted(p_list, key=lambda patch: (patch.database_name, patch.major, patch.minor))

    def non_existing_databases(scripts):
        """ We try to connect to the databases in the input list of patches.
        If we fail to connect, the database is included in result.

        :param scripts: A list of patch files.
        :return: A list of nonexistent databases.
        """
        result = []
        # Try to connect to the databases
        for script in scripts:
            database_name = script.database_name
            user = script.user
            pwd = password_for_user(script.user, prefix)
            try:
                database_connection(database_name, user, pwd)
            except OperationalError:
                logging.debug(f"Adding {database_name} to list of non existing databases")
                result.append(database_name)
        return result

    def apply_patch(patch):
        """ Executes a patch using psycopg2. If successful the script results will be committed, otherwise rolled back.

        :param patch: The patch to apply.
        :return: Nothing
        :raises: Exception: Rethrown from psycopg2. Should maybe be OperationalError?
        """
        logging.debug(f"Executing {patch.major}.{patch.minor}.{patch.name} on database {patch.database_name}")

        def database_connection_patch():
            """ Creates a database connection for the patch.

            :return: A connection using credentials in patch
            """
            database_name = patch.database_name
            user = patch.user
            pwd = password_for_user(patch.user, prefix)
            return database_connection(database_name, user, pwd)

        with database_connection_patch() as connection:
            with connection.cursor() as cursor:
                file_name = patch.sql_file
                with open(file_name, "r") as f:
                    sql = f.read()
                    try:
                        cursor.execute(sql)
                    except Exception as e1:
                        logging.error(f'Failed updating database {patch.database_name}. Errors in script {file_name}')
                        connection.rollback()
                        raise e1

            connection.commit()

    def create_databases(create_patches):
        """ Executes all baseline scripts.

        :param create_patches: A list of Patches representing the baseline scripts (major=00000000).
        :return: A tuple. The first value indicates if successful, the second is the list of exeuted patches.
        """
        try:
            executed_patches = []

            for patch in create_patches:
                user = patch.user
                if patch.minor == '0000':
                    logging.debug(f"Executing {patch.major}.{patch.minor}.{patch.name} on database {patch.database_name}")
                    # First file is from a pg_dump. We need to run these through psql
                    psql = shutil.which("psql")
                    if psql is None:
                        logging.error("psql program must be found on PATH")
                        exit(1)
                    # If the script wants to create a role with the same name as the database, read the password from
                    # environment variable and pass it to the script
                    os.environ['PATCHES_POSTGRESQL_TEMPORARY_USER_PASSWORD'] = password_for_user(patch.database_name, prefix)
                    os.environ['PGPASSWORD'] = password_for_user(patch.user, prefix)
                    process = subprocess.Popen([psql, "-f", patch.sql_file, "postgres", user],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               universal_newlines=True,
                                               shell=False)
                    try:
                        outs, errs = process.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        outs, errs = process.communicate()
                    if errs is not None and len(errs) != 0:
                        #  Basesline failed
                        logging.warning(outs)
                        logging.error(errs)
                        raise Exception(f"Failed creating database {patch.database_name}. "
                                        f"Errors in baseline script {patch.sql_file}")
                    else:
                        logging.debug(outs)
                        logging.debug(errs)
                else:
                    # run psycopg2
                    apply_patch(patch)
                executed_patches.append(patch)
            return True, executed_patches
        except Exception as e1:
            logging.error(f"Failed creating a database. You will have to drop the database manually. Error: {e1}")
            return False, []

    def update_patches_in_database(executed_patches, connection):
        """ Updates the patch database with all patches in executed_patches.

        :param executed_patches: A list of executed patches.
        :param connection: The connection to the patch database.
        :return: Nothing
        """
        for patch in executed_patches:
            logging.info(f'Saving executed patch {patch.name} version {patch.major}.{patch.minor} '
                         f'for database {patch.database_name}')
            with connection.cursor() as cur:
                cur.execute("CALL sp_patch_installed(%s, %s, %s, %s);",
                            (patch.database_name, patch.major, patch.minor, patch.name))

    def apply_new_patches(patches, connection):
        """ Applies all included patches if they are not already stored in patch database.

        :param patches: A list of patches to execute.
        :param connection: The connection to use.
        :return: A tuple. The first value indicates if successful, the second is the list of exeuted patches.
        """
        applied_patches = []
        try:
            for patch in patches:
                with connection.cursor() as cur:
                    cur.execute("SELECT fn_patch_installed(%s, %s, %s)", (patch.database_name, patch.major, patch.minor))
                    count = cur.fetchone()[0]
                    # All patches executed in function create_databases() will return 1 count, and not be executed again
                    if count == 0:
                        apply_patch(patch)
                        applied_patches.append(patch)
        except Exception as e:
            logging.error(f"Caught exception, nu further scripts executed. Exception: {e}")
            return False, applied_patches
        return True, applied_patches

    try:
        patches_list = []
        logging.debug(f"PARENT_PATH={PARENT_PATH}")
        self_glob = PARENT_PATH.glob('*.sql')
        logging.debug(f"self_glob={self_glob}")
        for p in self_glob:
            logging.debug(f"Found patch file {p}")
            patches_list.append(p)
        for g in globs:
            logging.debug(f"g={g}")
            files = glob.glob(g)
            if len(files) == 0:
                raise Exception("No files found for {}".format(g))
            for file in files:
                logging.debug(f"Found patch file {file}")
                patches_list.append(file)

        all_scripts = all_scripts_sorted(patches_list)
        for i in range(1, len(all_scripts)):
            previous = all_scripts[i - 1]
            current = all_scripts[i]
            if previous.database_name == current.database_name and \
                    previous.major == current.major and \
                    previous.minor == current.minor:
                raise Exception(f'Scripts {previous.name} and {current.name} have same '
                                f'major={previous.major} and minor={previous.minor}')
        # Only first script for each database
        create_scripts = filter(lambda patch: patch.major == '00000000' and patch.minor == '0000', all_scripts)
        databases_to_create = non_existing_databases(create_scripts)
        init_scripts = \
            filter(lambda patch: patch.database_name in databases_to_create and patch.major == '00000000', all_scripts)
        success, executed_init_scripts = create_databases(init_scripts)
        if not success:
            return False
        # Now the patches database exists, we can start using it
        password = password_for_user(PATCHES, prefix)
        with database_connection(PATCHES, PATCHES, password) as patches_connection:
            # Store applied patches from initialization
            update_patches_in_database(executed_init_scripts, patches_connection)
            # Each patch is checked with the patch database and executed only once
            remaining_patches = filter(lambda patch: patch.major != '00000000', all_scripts)
            success, new_patches = apply_new_patches(remaining_patches, patches_connection)
            update_patches_in_database(new_patches, patches_connection)
            patches_connection.commit()
            return success
    except Exception as e:
        logging.error(e)
        return False


if __name__ == '__main__':
    # Test installation of patches database by itself
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)-7s %(module)s %(message)s')
    apply_patches([], "POSTGRESQL_")
