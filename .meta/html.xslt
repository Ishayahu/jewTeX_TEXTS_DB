<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml" xmlns:svg="http://www.w3.org/2000/svg">

<xsl:output method="xml" indent="yes"
        doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
        doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>


<xsl:template match="/">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ru" lang="ru">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>test1</title>
    <style type="text/css">
      .work_needed{ background: DarkOrange;}
      /*.link_needed{ background: red;}
      .term {text-decoration: underline;}
      .comment {font-size: small;
                font-style: italic;}*/
      .summary {font-style: italic;}
      .posuk_p p{display: inline}
      .makshan{
        background-color: #ff6666;
      }
      .tarzan{
        background-color: #66ff66;
      }
      .halacha{
        text-decoration: underline;
        font-weight: bold;
      }
      .NaN{background-color: black}
      .Red{background-color: red}
      .Green{background-color: green}
      .Yellow{background-color: yellow}
      .Lightgreen{background-color: lightgreen}
      .Indigo{background-color: indigo; color: white}
      table{border: 1px black solid}
      td, th {
        border-left: 1px solid #999;
        border-top: 1px solid #999;
        }
      .diagonal-split {
        position: relative;
        min-width: 150px;
        height: 80px;
        background: linear-gradient(
          to top right,
          transparent 49.5%,
          #000 50%,
          transparent 50.5%
        );
      }

      .top-right {
        position: absolute;
        top: 5px;
        right: 5px;
        text-align: right;
        width: 45%;
      }

      .bottom-left {
        position: absolute;
        bottom: 5px;
        left: 5px;
        width: 45%;
      }
      .img-container{display: flow-root}
      .img-title{font-style: italic}
      svg{
        width: 100%;
        height: 100%;
        display: block;
      }
      .svg-container{
        width: 100%;
        height: 100vh; /* Занимает всю высоту экрана */
        overflow: auto; /* Добавляет скролл при зуме */
        position: relative;
  
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
        <h2>Глава <xsl:value-of select="@number"/>: 
			<xsl:choose>
				<xsl:when test="@verbouse_name">
					<xsl:value-of select="@verbouse_name"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="@name"/>
				</xsl:otherwise>
			</xsl:choose>	
		</h2>
		<xsl:apply-templates />
    </xsl:template>
    
    <xsl:template match="header[@type='sub_chapter']">
        <h2>Раздел <xsl:value-of select="@number"/>: 
			<xsl:choose>
				<xsl:when test="@verbouse_name">
					<xsl:value-of select="@verbouse_name"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="@name"/>
				</xsl:otherwise>
			</xsl:choose>	
		</h2>
		<xsl:apply-templates />
    </xsl:template>

    <xsl:template match="page">
        <h4>стр. <xsl:value-of select="@name"/></h4>
		<xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="header[@type='letter']">
        <h4><xsl:value-of select="@name"/></h4>
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
		<a>
			<xsl:attribute name='name'><xsl:value-of select="generate-id()"/></xsl:attribute>
			<h3 data-type='header'>
				<xsl:attribute name='data-level'><xsl:value-of select="@level" /></xsl:attribute>
				<xsl:value-of select="@name"/>: <xsl:value-of select="@verbouse_name"/>
			</h3>	
		</a>
		<xsl:apply-templates />
    </xsl:template>
    <xsl:template match="header[@type='seif']">
		<a>
			<xsl:attribute name='name'><xsl:value-of select="generate-id()"/></xsl:attribute>
			<h4 data-type='header'>
				<xsl:attribute name='data-level'><xsl:value-of select="@level" /></xsl:attribute>
				<xsl:value-of select="@name"/>: <xsl:value-of select="@verbouse_name"/>
			</h4>
		</a>
		<xsl:apply-templates />
    </xsl:template>
    <xsl:template match="header[@type='siman_katan']">
		<a>
			<xsl:attribute name='name'><xsl:value-of select="generate-id()"/></xsl:attribute>
			<h5 data-type='header'>
				<xsl:attribute name='data-level'><xsl:value-of select="@level" /></xsl:attribute>
				<xsl:value-of select="@name"/>: <xsl:value-of select="@verbouse_name"/>
			</h5>
		</a>
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
      <xsl:choose>
        <xsl:when test="@reason">
          <span class="work_needed">
            <xsl:attribute name='title'><xsl:value-of select="@reason" /></xsl:attribute>
            <xsl:apply-templates/>
          </span>
        </xsl:when>
        <xsl:otherwise>
          <span class="work_needed" title="Нужно доработать текст">
            <xsl:apply-templates/>
          </span>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:template>

    <xsl:template match="term">
        <span class="term">
			<xsl:if test="@name">
				<xsl:attribute name='name'><xsl:value-of select="@name" /></xsl:attribute>
			</xsl:if>
            <xsl:apply-templates/>
        </span>
    </xsl:template>
    <xsl:template match="halacha">
        <p class="halacha">
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <xsl:template match="makshan">
        <div class="makshan">
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <xsl:template match="tarzan">
        <div class="tarzan">
            <xsl:apply-templates/>
        </div>
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
    
    <xsl:template match="img">
      <div class='img-container'>
        <xsl:copy-of select="."/>
      </div>
      <div class='img-title'>
        Рис. <xsl:number 
            level="any" 
            count="img|svg:svg" 
            format="1." 
            letter-value="traditional"/>: <xsl:value-of select="@alt" />
      </div>
    </xsl:template>
    <xsl:template match="div">
      <div class='svg-container'>
        <xsl:copy-of select="."/>
      </div>
    </xsl:template>
    
    <xsl:template match="svg:*">
      <xsl:copy>
        <xsl:copy-of select="."/>
      </xsl:copy>
      <div class='img-title'>
        Рис. <xsl:number 
            level="any" 
            count="img|svg:svg" 
            format="1." 
            letter-value="traditional"/>: <xsl:value-of select="@alt" />
      </div>

    </xsl:template>
    
    
    <xsl:template match="ol">
      <ol>
        <xsl:copy-of select="@*"/>
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
    <xsl:variable name="comment_number">
      <xsl:number level="any" count="comment"/>
    </xsl:variable>
    <span class="comment"><xsl:attribute name='title'><xsl:value-of select="$comment_number"/></xsl:attribute>
      <sup>
        <xsl:attribute name='id'><xsl:value-of select="concat('sup',$comment_number)"/></xsl:attribute>
        <strong>
          <xsl:value-of select="$comment_number"/>
        </strong>
      </sup>
      <span class='comment_text'>
        <xsl:if test="$comment_number">
          <xsl:attribute name='id'><xsl:value-of select="concat('comment',$comment_number)"/></xsl:attribute>
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
    <xsl:template match="s">
        <s>
            <xsl:apply-templates/>
        </s>
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
    
    <xsl:template match="table">
      <xsl:copy>
        <!-- Копируем атрибуты и пространства имен -->
        <!-- <xsl:apply-templates select="@*"/> -->
        
        <!-- Обрабатываем содержимое таблицы -->
        <xsl:apply-templates select="*|text()"/>
      </xsl:copy>
      <div class='img-title'>
        Таб. <xsl:number 
            level="any" 
            count="table" 
            format="1." 
            letter-value="traditional"/>: <xsl:value-of select="@alt" />
      </div>


    </xsl:template>
    <xsl:template match="tr">
      <tr>
        <xsl:apply-templates/>
      </tr>
    </xsl:template>
    <xsl:template match="th">
      <th>
        <xsl:copy-of select="@*"/>
        <xsl:apply-templates/>
      </th>
    </xsl:template>
    <xsl:template match="td">
      <td>
        <xsl:copy-of select="@*"/>
        <xsl:apply-templates/>
      </td>
    </xsl:template>


    <xsl:template match="quote">
		<div class="quote">
			<!-- <xsl:copy-of select="."> -->
			<!-- </xsl:copy-of> -->
			<xsl:apply-templates/>
		</div>
    </xsl:template>
    
    <xsl:template match="spoiler">
		<div class="spoiler">
			<xsl:apply-templates/>
		</div>
    </xsl:template>

    <xsl:template match="external_link">
        <a target='_blank' ><xsl:attribute name='href'><xsl:value-of select="@url"/></xsl:attribute><xsl:value-of select="@name"/></a>
    </xsl:template>
	
</xsl:stylesheet>