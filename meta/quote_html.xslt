<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">

<xsl:output method="xml" indent="yes"/>


    <xsl:template match="/">
        <span>
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="header[@type='ref']">
            <xsl:text />
            <xsl:apply-templates />
    </xsl:template>

    <xsl:template match="quote">
        <xsl:copy-of select=".">
        </xsl:copy-of>
    </xsl:template>

    <xsl:template match="work_needed">
        <span class="work_needed">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

</xsl:stylesheet>