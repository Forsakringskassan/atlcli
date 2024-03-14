# Some useful tools
## Short description of the scripts
### atlcli tool select-columns
For each input line outputs the selected columns.
### atlcli tool count-group-by
For the selected columns, counts the number of lines having the same value.
### atlcli tool where-matches
For each input line compares the selected column to a value.
### atlcli tool join-columns
Joins input with a named file.
### atlcli tool where-columns
For each input line compares two columns.
### atlcli bitb order-by
Sorts the input on a selected column.
### atlcli bitb minus-columns
Remove rows from input matching rows in named file.
### atlcli tool compare-versions
Compares version numbers.
## atlcli tool select-columns
```
$ atlcli tool select-columns --help
usage: python -m atlcli tool select-columns [-h] [-l FILE] [-a SEPARATOR]
                                            column [column ...]

For each input line outputs the selected columns.

positional arguments:
  column                column number to include in output.

options:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin.
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides.

Output is the selected input columns in the order defined by the arguments.
```
## atlcli tool count-group-by
```
$ atlcli tool count-group-by --help
usage: atlcli tool count-group-by [-h] [-l FILE] [-a SEPARATOR] column [column ...]

For the selected columns, counts the number of lines having the same value.

positional arguments:
  column                column number to include in computation.

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Output is the selected input columns and the number of times they occurr.
```
## atlcli tool where-matches
```
$ atlcli tool where-matches --help
usage: atlcli tool where-matches [-h] [-l FILE] [-a SEPARATOR] column value

For each input line compares the selected column to a value.

positional arguments:
  column                Column number to compare.
  value                 Regular expression to compare column value to.

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Output is the selected input lines where the column value matches the
parameter.
```
## atlcli tool join-columns
```
$ atlcli tool join-columns --help
usage: atlcli tool join-columns [-h] [-l FILE] [-a SEPARATOR] join [column ...]

Joins input with a named file.

positional arguments:
  join                  Name of file to join.
  column                Column number to join. Order is not important. If not
                        given, all columns in join file are included (default:
                        None)

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Output is only those rows having matching column values in both input and join
file. All columns from input file and join file are output, the columns from
the join file after the columns from input.
```
## atlcli bitb where-columns
```
$ atlcli tool where-columns--help
usage: atlcli tool where-columns[-h] [-l FILE] [-a SEPARATOR] first condition second

For each input line compares two columns.

positional arguments:
  first                 First column number to compare.
  condition             Condition for comparison.
  second                Second column to compare.

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Output is the input lines where the column values matches the condition.
```
### Analyze which repos have problems in jenkins
```
$ atlcli bitb get-projects | grep _FUSE_ | grep -v TOOLS | atlcli bitb get-repos | egrep '\-app' > repon.txt
$ cat repon.txt | atlcli bitb get-tags -d -n 'v\d+\.\d+\.\d+' > taggade-repon.txt
$ cat repon.txt | atlcli bitb get-tags -d -n 'v\d+\.\d+\.\d+-RC' > rc-repon-tags.txt
$ cat rc-repon-tags.txt | sed "s/-RC//" > rc-repon.txt
$ cat rc-repon.txt | atlcli tool join-columns taggade-repon.txt 0 1 | atlcli tool where-columns 2 "!=" 3
v1.17.3 v1.17.2 arendehantering-registerutdrag-app  APPII_FUSE_AHS        
v1.3.1  v1.3.0  extinf-migrationsverket-app APPII_FUSE_EXT       
v1.6.0  v1.5.0  extinf-ssbt-v4-app APPII_FUSE_EXT        

```


## atlcli bitb order-by
```
$ atlcli bitb order-by --help
usage: atlcli bitb order-by [-h] [-l FILE] [-i] [-a SEPARATOR] COLUMN

Sorts the input on a selected column.

positional arguments:
  COLUMN                Column number to sort by.

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -i, --invert          Sorts output in decreasing order. (default: False)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Output contains all input rows.
```
## atlcli bitb minus-columns
```
$ atlcli bitb minus-columns --help
usage: atlcli bitb minus-columns [-h] [-l FILE] [-a SEPARATOR] minus [column ...]

Removes rows from input matching rows in named file.

positional arguments:
  minus                 Name of file to minus.
  column                Column number to minus. Order is not important. If not
                        given, all columns in minus file are included
                        (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Output is only those rows in input not having matching column values in named
file.

```
## atlcli tool compare-versions
```
$ atlcli tool compare-versions --help
usage: atlcli tool compare-versions [-h] [-b BINARY] FIRST SECOND

Compares version numbers.

positional arguments:
  FIRST                 First version to compare.
  SECOND                Second version to compare.

optional arguments:
  -h, --help            show this help message and exit
  -b BINARY, --binary BINARY
                        If given result is returned to shell as well as text
                        output. (default: None)

Output is a 1 if second version is higher than first version. 0 if they are
equal. -1 if first version is less than the second.
```

## xslt-transform.groovy
Transforms xmlfiles using xslt. 

Saxon HE (Java) is used. It is capable of xslt 3.0.
```
$ xsl-transform.groovy -h
usage: xsl-transform -x xsltFile [-t] [-i inputFile] [-o outputFile] [-e
                     extension] [-h] [file ...]
Transforms inputfile to outputfile, or a list of files, using transform
defined as parameter.
 -e,--extension <arg>   Used with lists of filenames to create a new
                        output filename
 -h,--help              Display usage
 -i,--input <arg>       Input file. If not defined stdin is used
 -o,--output <arg>      Output file. If not defined stdout is used
 -t,--trace             Print input and output file names
 -x,--xslt <arg>        Xslt definition file. Required.

```
### Xslt 3.0 identity transform transforms itself
```
$ cat identity.xsl
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
        version="3.0" >
        <xsl:output method="xml" indent="yes"/>
        <xsl:mode on-no-match="shallow-copy"/>
</xsl:stylesheet>

$ xsl-transform.groovy -x identity.xsl -i identity.xsl
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
                version="3.0">
   <xsl:output method="xml" indent="yes"/>
   <xsl:mode on-no-match="shallow-copy"/>
</xsl:stylesheet>
```
### Extracts all endpoints from pom files
First use some xslt magic to extract the information from the pom files.
```
$ cat APPII_FUSE_TOOLS/build/xslt/endpoints.xsl
<?xml version="1.0" encoding="UTF-8"?>
<!-- Skapar en textfil med alla beroenden i en pomfil -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
        version="3.0" >
        <xsl:output method="text"/>
        <xsl:mode on-no-match="shallow-skip"/>
        <xsl:template match="/"><xsl:apply-templates/></xsl:template>
        <xsl:template match="/project/build/plugins/plugin[artifactId='xy-fuse-profile-tool-plugin']/configuration/endpoints/endpoint[path!='/int/person/personsituation/1/hittakunder/pnr/%s']/path"><xsl:value-of select="../../../../../../../name"/><xsl:text> </xsl:text> <xsl:value-of select="."/><xsl:text>&#xd;&#xa;</xsl:text></xsl:template>
</xsl:stylesheet>

$ atlcli bitb get-projects | grep _FUSE_ | atlcli bitb get-repos | dos2unix | sed "s/\s/\//g" | sed "s/$/\/pom.xml/g" | xargs xsl-transform.groovy -e endpoints -x /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/endpoints.xsl
$ cat */*/pom.endpoints > endpoints.txt
```
Now we can count the number endpoints for each integration, and select those having only one.
```
$ cat endpoints.txt | atlcli tool count-group-by 0 | atlcli tool where-matches 1 1 > enkla.txt
$ head enkla.txt
sjp-utbetalningar-kommande-app   1
tfp-anledningar-app      1
tfp-dagar-uttagna-app    1
tfp-kompletterande-uppgifter-app         1
arendestyrning-akt-app   1
arkivering-imagearkiv-dokument-app       1
aktivitetsstod-beslut-app        1
aktivitetsstod-provning-app      1
extinf-lefi-app          1
extinf-migrationsverket-app      1

```
And finally joint the results.

```
$ cat endpoints.txt | atlcli tool join-columns enkla.txt 0 | atlcli tool select-columns 0 1 > simple-endpoints.txt
$ head simple-endpoints.txt
sjp-utbetalningar-kommande-app  /
tfp-anledningar-app     /tuxedo/tfpVHsbAnledn
tfp-dagar-uttagna-app   /tuxedo/tfpVHsbKalender
tfp-kompletterande-uppgifter-app        /tuxedo/tfpVHsbKompInfo
arendestyrning-akt-app  /tuxedo/astHAkt
arkivering-imagearkiv-dokument-app      /
aktivitetsstod-beslut-app       /asu-ufa-fasad-web/rest/v1/avstangningsimpuls/%s
aktivitetsstod-provning-app     /asu-akassasituation-app/ArbetsvillkorService_v1
extinf-lefi-app /
extinf-migrationsverket-app     /ws/XY.MIV.xyindividunderlag.v2
```


### Changes master pom version to 1.12.0 in all repos
```
$ cat  /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/version-fix.xsl
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
        version="3.0" >
        <xsl:output method="xml" indent="yes"/>
        <xsl:mode on-no-match="shallow-copy"/>
        <xsl:template match="/project/parent/version">
                <xsl:copy>1.12.0</xsl:copy>
        </xsl:template>
</xsl:stylesheet>
$ atlcli bitb get-projects | grep _FUSE_ | atlcli bitb get-repos | dos2unix | sed "s/\s/\//g" | sed "s/$/\/pom.xml/g" | \
xargs xsl-transform.groovy -x /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/version-fix.xsl
```
### Retrieves all dependencies in all Fuse repos
```
$ cat  /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/dependencies.xsl
<?xml version="1.0" encoding="UTF-8"?>
<!-- Creates at plain text file containing dependencies from a pom file -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
        version="3.0" >
        <xsl:output method="text"/>
        <xsl:mode on-no-match="shallow-skip"/>
        <xsl:template match="/"><xsl:apply-templates/></xsl:template>
        <!-- Some versions are coded as properties -->
        <xsl:template match="/project/properties/*[matches(name(), '.*\.version$')]"><xsl:value-of select ="name(.)"/><xsl:text> </xsl:text><xsl:copy-of select="."/><xsl:text>&#xa;</xsl:text></xsl:template>
        <!-- Plain old dependencies -->
        <xsl:template match="/project/dependencies/dependency"><xsl:value-of select="./groupId"/><xsl:text> </xsl:text><xsl:value-of select="./artifactId"/><xsl:text> </xsl:text><xsl:value-of select="./version"/><xsl:text>&#xa;</xsl:text></xsl:template>
        <!-- Build dependencies -->
        <xsl:template match="/project/build/plugins/plugin"><xsl:value-of select="./groupId"/><xsl:text> </xsl:text><xsl:value-of select="./artifactId"/><xsl:text> </xsl:text><xsl:value-of select="./version"/><xsl:text>&#xa;</xsl:text></xsl:template>
</xsl:stylesheet>
$ atlcli bitb get-projects | grep _FUSE_ | atlcli bitb get-repos | dos2unix | sed "s/\s/\//g" | sed "s/$/\/pom.xml/g" | \
xargs xsl-transform.groovy -e txt -x /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/dependencies.xsl
$ cat */*/pom.txt | sort | uniq | tail -n8
spring.version x.y.z
swagger.codegen.version x.y.z
testutil.version x.y.z
testutil.version x.y.z
uk.org.lidalia slf4j-test x.y.z
weblogic wlthint3client ${wls.version}
wls.version x.y.z
wls.version x.y.z
```
### Updates version in pom.xml for all repos needing update
This is the xslt we are going to use.
```
$ cat /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/update-version.xsl
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
        version="3.0" >
        <xsl:output method="xml" indent="yes"/>
        <xsl:mode on-no-match="shallow-copy"/>
        <xsl:template match="/project/version">
                <xsl:copy><xsl:value-of select="environment-variable('newversion')"/><xsl:text>${revision}</xsl:text></xsl:copy>
        </xsl:template>
</xsl:stylesheet>
```
We can find which develop branches has changed since latest release tag with the filter-merged script. We save the
results for later use.
```
$ atlcli bitb get-projects | grep _FUSE_ | atlcli bitb get-repos | atlcli bitb get-branches-or-tags -n develop "^v\d+\.\d+\.\d+$" | \
atlcli bitb filter-merged -i > needs-version-update.txt
```
We extract the current release version and feed that to the bash script creating a new version number storing it
in environment variable newversion.
```
$ (set -e && set -o pipefail && cat needs-version-update.txt | grep _FUSE_ | atlcli bitb get-tags -n "^v\d+\.\d+\.\d+$" | \
sed "s/refs\/tags\/v//g" | sed -E 's/([0-9]+)\.([0-9]+)\.([0-9]+)/\1\t\2\t\3/' | dos2unix | \
while IFS=$'\t' read proj repo major minor revision; do pushd $proj/$repo; let newminor=$minor+1; \
oldversion="$major.$minor.$revision"; export newversion="$major.$newminor.0"; echo "old=$oldversion,new=$newversion"; \
[[ -f pom.xml ]] && xsl-transform.groovy -x /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/update-version.xsl pom.xml; popd; done)
```
### Updates all pomfile dependencies to current release version
Create start of xslt-file:
```
$ echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
 <xsl:stylesheet xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"
 xpath-default-namespace=\"http://maven.apache.org/POM/4.0.0\"
 version=\"3.0\" >
 <xsl:output method=\"xml\" indent=\"yes\"/>
 <xsl:mode on-no-match=\"shallow-copy\"/>" > update-api-versions.xsl
```
Add a row for each api repo:
```
atlcli bitb get-projects | grep FUSE | egrep -v 'CORE|TOOLS' | atlcli bitb get-repos | grep api | atlcli bitb get-tags -n "^v\d+\.\d+\.\d+$" -d | sed -E 's/v([0-9\.]+)/\1/g' | dos2unix.exe | while IFS=$'\t' read proj repo version; do echo "<xsl:template match=\"/project/dependencies/dependency[artifactId='$repo']/version\"><xsl:copy>$version</xsl:copy></xsl:template>"; done >> update-api-versions.xsl
```
Create the end of the file:
```
echo "</xsl:stylesheet>" >> update-api-versions.xsl
```
Apply the xslt:
```
$ atlcli bitb get-projects | grep _FUSE_ | egrep -v 'CORE|TOOLS' | atlcli bitb get-repos | egrep -v 'master|api' | dos2unix | sed "s/\s/\//g" | sed "s/$/\/pom.xml/g" | xargs xsl-transform.groovy -x /c/SecretPath/repo/git/icc/fuse/APPII_FUSE_TOOLS/build/xslt/update-api-versions.xsl
```
### Updates all pomfile dependencies to current snapshot version
Create start of xslt file
```
$ echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<xsl:stylesheet xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"
xpath-default-namespace=\"http://maven.apache.org/POM/4.0.0\"
version=\"3.0\" >
<xsl:output method=\"xml\" indent=\"yes\"/>
<xsl:mode on-no-match=\"shallow-copy\"/>" > update-versions.xsl
```
Find all repos where snapshot is newer than release, and create an xslt entry for each
```
$ grep -E "api|util" needs-version-update.txt | grep -v CORE | dos2unix.exe | atlcli bitb get-tags -n "^v\d+\.\d+\.\d+$" | \
sed "s/refs\/tags\/v//g" | sed -E 's/([0-9]+)\.([0-9]+)\.([0-9]+)/\1\t\2\t\3/' | \
while IFS=$'\t' read proj repo major minor revision; do let newminor=$minor+1; oldversion="$major.$minor.$revision"; \
export newversion="$major.$newminor.0"; \
echo "<xsl:template match=\"/project/dependencies/dependency[artifactId='$repo']/version\"><xsl:copy>$newversion-SNAPSHOT</xsl:copy></xsl:template>"; done >> update-versions.xsl
```
Add xslt end of file
```
$ echo "</xsl:stylesheet>" >> update-versions.xsl
```
Apply the xslt
```
$ atlcli bitb get-projects | grep _FUSE_ | atlcli bitb get-repos | dos2unix | sed "s/\s/\//g" | sed "s/$/\/pom.xml/g" | \
xargs xsl-transform.groovy -x /c/SecretPath/repo/git/icc/fuse/update-versions.xsl
```
### Finds missing version tags
```
$ atlcli bitb get-projects | grep _FUSE_ | atlcli bitb get-repos | atlcli bitb get-branches-or-tags -n "^v\d+\.\d+\.\d+-RC$"  "^v\d+\.\d+\.\d+$" | atlcli bitb filter-merged -i > wrong-release.txt
$ cat wrong-release.txt
APPII_FUSE_CORE domanmodell-api refs/tags/v1.8.0-RC refs/tags/v1.6.0
APPII_FUSE_CORE infrastruktur-api refs/tags/v1.6.0-RC refs/tags/v1.5.1
APPII_FUSE_KUI organisation-anvandarinformation-api refs/tags/v1.0.1-RC refs/tags/v1.0.0
APPII_FUSE_KUI organisation-anvandarinformation-app refs/tags/v1.0.1-RC refs/tags/v1.0.0
APPII_FUSE_KUI organisation-behorigheter-api refs/tags/v1.3.0-RC refs/tags/v1.2.0
APPII_FUSE_KUI organisation-behorigheter-app refs/tags/v1.5.0-RC refs/tags/v1.3.0
APPII_FUSE_KUI organisation-bestallningsunderlag-api refs/tags/v1.1.0-RC refs/tags/v1.0.0
APPII_FUSE_KUI organisation-bestallningsunderlag-app refs/tags/v1.4.0-RC refs/tags/v1.3.0
APPII_FUSE_KUI organisation-organisationsinformation-api refs/tags/v1.0.1-RC refs/tags/v1.0.0
APPII_FUSE_KUI organisation-organisationsinformation-app refs/tags/v1.0.1-RC refs/tags/v1.0.0
APPII_FUSE_KND hittakunder-util refs/tags/v1.1.0-RC refs/tags/v1.0.2
APPII_FUSE_KND person-personbasinfo-app refs/tags/v1.1.0-RC refs/tags/v1.0.0
$ cat wrong-release.txt | atlcli bitb get-tags  -n "^v\d+\.\d+\.\d+-RC$" | atlcli bitb get-commits | sed "s/-RC//" | sed "s/refs\/tags\///" | dos2unix | \
while IFS=$'\t' read proj repo version commit; do echo "$proj $repo dummy $commit" | atlcli bitb create-tags $version; done
APPII_FUSE_CORE domanmodell-api refs/tags/v1.8.0
APPII_FUSE_CORE infrastruktur-api refs/tags/v1.6.0
APPII_FUSE_KUI organisation-anvandarinformation-api refs/tags/v1.0.1
APPII_FUSE_KUI organisation-anvandarinformation-app refs/tags/v1.0.1
APPII_FUSE_KUI organisation-behorigheter-api refs/tags/v1.3.0
APPII_FUSE_KUI organisation-behorigheter-app refs/tags/v1.5.0
APPII_FUSE_KUI organisation-bestallningsunderlag-api refs/tags/v1.1.0
APPII_FUSE_KUI organisation-bestallningsunderlag-app refs/tags/v1.4.0
APPII_FUSE_KUI organisation-organisationsinformation-api refs/tags/v1.0.1
APPII_FUSE_KUI organisation-organisationsinformation-app refs/tags/v1.0.1
APPII_FUSE_KND hittakunder-util refs/tags/v1.1.0
APPII_FUSE_KND person-personbasinfo-app refs/tags/v1.1.0
```