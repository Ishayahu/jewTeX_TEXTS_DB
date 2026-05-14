<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml" xmlns:svg="http://www.w3.org/2000/svg">

  <!-- <xsl:output method="xml" indent="yes" -->
          <!-- doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" -->
          <!-- doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/> -->


  <xsl:template match="/">
    <article>
      <xsl:apply-templates/>
    </article>
  </xsl:template>

  <xsl:template match="td">
    |<xsl:apply-templates />|
    <!-- <xsl:apply-templates /> -->
  </xsl:template>

</xsl:stylesheet>