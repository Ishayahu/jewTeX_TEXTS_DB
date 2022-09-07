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
                    /*.link_needed{ background: red;}
                    .term {text-decoration: underline;}
                    .comment {font-size: small;
                                font-style: italic;}*/
					.summary {font-style: italic;}
					.posuk_p p{display: inline}
					.makshan{
						color: red;
					}
					.tarzan{
						color: green;
					}
					.halacha{
						text-decoration: underline;
						font-weight: bold;
					}
                </style>
            </head>
            <body>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="header[@type='part']">
        <h2>Часть <xsl:value-of select="@number"/>: <xsl:value-of select="@verbouse_name"/></h2>
		<xsl:apply-templates />
    </xsl:template>

    <xsl:template match="header[@type='gate']">
        <h2>Врата <xsl:value-of select="@number"/>: <xsl:value-of select="@verbouse_name"/></h2>
		<xsl:apply-templates />
    </xsl:template>

    <xsl:template match="header[@type='chapter']">
        <h2>Глава <xsl:value-of select="@number"/>: <xsl:value-of select="@verbouse_name"/></h2>
		<xsl:apply-templates />
    </xsl:template>

    <xsl:template match="page">
        <h4>стр. <xsl:value-of select="@name"/></h4>
		<xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="header[@type='letter']">
        <h3><xsl:value-of select="@name"/></h3>
        <p>
            <xsl:apply-templates />
        </p>
    </xsl:template>
	<!--  -->
    <xsl:template match="header[@type='posuk']">
        <p><strong><xsl:value-of select="@name"/></strong>
            <xsl:apply-templates />
        </p>
    </xsl:template>
	
    <xsl:template match="header[@type='siman']">
        <h2><xsl:value-of select="@name"/>: <xsl:value-of select="@verbouse_name"/></h2>
		<xsl:apply-templates />
    </xsl:template>
    <xsl:template match="header[@type='seif']">
        <h3><xsl:value-of select="@name"/>: <xsl:value-of select="@verbouse_name"/></h3>
		<xsl:apply-templates />
    </xsl:template>
    <xsl:template match="header[@type='siman_katan']">
        <h3><xsl:value-of select="@name"/>: <xsl:value-of select="@verbouse_name"/></h3>
		<xsl:apply-templates />
    </xsl:template>
	
    <xsl:template match="summary">
        <h3><xsl:value-of select="@type"/></h3>
		<div class='summary'>
			<xsl:apply-templates />
		</div>
    </xsl:template>

    <xsl:template match="link_needed">
        <span class="link_needed" title='нужно проставить ссылки'>
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="work_needed">
        <span class="work_needed" title='нужно доработать текст'>
            <xsl:apply-templates/>
        </span>
    </xsl:template>

    <xsl:template match="term">
        <span class="term">
            <xsl:apply-templates/>
        </span>
    </xsl:template>
    <xsl:template match="halacha">
        <p class="halacha">
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <xsl:template match="makshan">
        <p class="makshan">
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <xsl:template match="tarzan">
        <p class="tarzan">
            <xsl:apply-templates/>
        </p>
    </xsl:template>
	

    <xsl:template match="p">
		<xsl:variable name="padding_base" select="20" />
		<xsl:variable name="level" select="@offset" />
		<xsl:variable name="padding_value" select="$level * $padding_base" />
        <p>
			<xsl:if test="@offset">
				<xsl:attribute name='style'><xsl:value-of select="concat('padding-left: ',$padding_value,'px;')" /></xsl:attribute>
			</xsl:if>
			<xsl:if test="@work_needed">
				<xsl:attribute name='class'>work_needed</xsl:attribute>
			</xsl:if>
            <xsl:apply-templates/>
        </p>
    </xsl:template>
	
    <xsl:template match="quoted_text">
        <p class='quote'>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

	
    <xsl:template match="sha">
        <strong>
            <xsl:apply-templates/>
        </strong>
    </xsl:template>
    <xsl:template match="mishna">
        <strong>
            <xsl:apply-templates/>
        </strong>
    </xsl:template>
    <xsl:template match="ol">
        <ol>
            <xsl:apply-templates/>
        </ol>
    </xsl:template>
    <xsl:template match="ul">
        <ul>
            <xsl:apply-templates/>
        </ul>
    </xsl:template>
    <xsl:template match="li">
        <li>
            <xsl:apply-templates/>
        </li>
    </xsl:template>

    <xsl:template match="comment">
        <span class="comment"><xsl:attribute name='title'><xsl:value-of select="@number"/></xsl:attribute>
            <sup>
				<xsl:attribute name='id'><xsl:value-of select="concat('sup',@number)"/></xsl:attribute>
				<strong>
				<xsl:value-of select="@number"/>
				</strong>
			</sup>
			<span class='comment_text'>
				<xsl:if test="@number">
					<xsl:attribute name='id'><xsl:value-of select="concat('comment',@number)"/></xsl:attribute>
				</xsl:if>
				<xsl:apply-templates/>
			</span>
        </span>
    </xsl:template>

    <xsl:template match="strong">
        <strong>
            <xsl:apply-templates/>
        </strong>
    </xsl:template>

    <xsl:template match="possible_comment">
        <span class="possible_comment">
            <xsl:apply-templates/>
        </span>
    </xsl:template>


    <xsl:template match="comment_needed">

        <span class="comment_needed" >

            <xsl:apply-templates/>
        </span>
        <span class="comment_needed_reason"><xsl:value-of select='@reason'/></span>
    </xsl:template>

    <xsl:template match="link">
        <xsl:copy-of select=".">
        </xsl:copy-of>

    </xsl:template>
    <xsl:template match="a">
        <xsl:copy-of select=".">
        </xsl:copy-of>

    </xsl:template>
    <xsl:template match="sup">
        <xsl:copy-of select=".">
        </xsl:copy-of>

    </xsl:template>

    <xsl:template match="quote">
		<div class="quote">
			<!-- <xsl:copy-of select="."> -->
			<!-- </xsl:copy-of> -->
			<xsl:apply-templates/>
		</div>
    </xsl:template>

    <xsl:template match="external_link">
        <a target='_blank' ><xsl:attribute name='href'><xsl:value-of select="@url"/></xsl:attribute><xsl:value-of select="@name"/></a>
    </xsl:template>
	
</xsl:stylesheet>