<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">

<xsl:output method="xml" indent="yes"
        doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
        doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>


<xsl:template match="/">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ru" lang="ru">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                <title>test1</title>
                <style type="text/css">
                    .link_needed{ background: red;}
                    .term {text-decoration: underline;}
                    .comment {font-size: small;
                                font-style: italic;}
                </style>
            </head>
            <body>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="header[@type='letter']">
        <h3><xsl:value-of select="@name"/></h3>
        <p>
            <xsl:apply-templates />
        </p>
    </xsl:template>

    <xsl:template match="link_needed">
        <span class="link_needed">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="work_needed">
        <span class="work_needed">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="term">
        <span class="term">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="p">
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match="comment">
        <span class="comment">
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="link">
        <xsl:copy-of select=".">
        </xsl:copy-of>

    </xsl:template>

    <xsl:template match="quote">
        <xsl:copy-of select=".">
        </xsl:copy-of>
    </xsl:template>


</xsl:stylesheet>