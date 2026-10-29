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
            <xsl:if test="@id"><xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute></xsl:if>
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <!-- Quote fragments do not include the main HTML stylesheet: keep box styles inline. -->
    <xsl:template match="p-ai">
        <p class="ai-translation"
           style="border: 1px dashed #b68b46; background-color: #fffaf0; padding: 0.75em 1em; margin: 0.75em 0; border-radius: 4px;">
            <xsl:if test="@id">
                <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
            </xsl:if>
            <span class="ai-translation-label"
                  style="display: block; color: #7b561d; font-size: 0.75em; font-weight: bold; margin-bottom: 0.5em;">Автоматический перевод · не проверен<xsl:if test="@id"><xsl:text> · </xsl:text><a href="#{@id}"><xsl:text>#</xsl:text><xsl:value-of select="@id"/></a></xsl:if></span>
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