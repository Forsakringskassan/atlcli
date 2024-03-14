<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	xpath-default-namespace="http://maven.apache.org/POM/4.0.0"
	version="3.0" >
	<xsl:output method="text"/>
	<xsl:mode on-no-match="deep-skip"/>
	<xsl:template match="/">
		<xsl:apply-templates select="project/version"/>
	</xsl:template>
	
	<xsl:template match="version"><xsl:copy-of select="."/></xsl:template>
</xsl:stylesheet>
