<?xml version="1.0"?>
<xsl:stylesheet xmlns:lace="http://heml.mta.ca/2019/lace" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml"/>
  <xsl:param name="identifier">FOO</xsl:param>
  <xsl:param name="classifier">FOO</xsl:param>
  <xsl:param name="rundate">FOO</xsl:param>
 <xsl:param name="engine">FOO</xsl:param>
  <xsl:template match="/">
    <lace:run>
      <dc:identifier>
        <xsl:value-of select="$identifier"/>
      </dc:identifier>
      <lace:classifier>
        <xsl:value-of select="$classifier"/>
      </lace:classifier>
      <dc:date>
        <xsl:value-of select="$rundate"/>
</dc:date>
<lace:ocrengine>
	<xsl:value-of select="$engine"/>
</lace:ocrengine>
      <lace:ocroutputtype>selected</lace:ocroutputtype>
    </lace:run>
  </xsl:template>
</xsl:stylesheet>
