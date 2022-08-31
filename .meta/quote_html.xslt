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
    <xsl:template match="p">
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <xsl:template match="strong">
        <strong>
            <xsl:apply-templates/>
        </strong>
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
    <xsl:template match="link">
        <xsl:copy-of select=".">
        </xsl:copy-of>

    </xsl:template>

    <xsl:template match="quote">
		<div class="quote">
			<xsl:copy-of select=".">
			</xsl:copy-of>
		</div>
    </xsl:template>


</xsl:stylesheet>