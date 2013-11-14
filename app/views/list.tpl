<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US"><meta charset="utf-8">
 <head>
    <!-- Standard Metadata -->
    <title>SBN Toolkit - Missing SBN</title>
    <meta name='abstract' content='' />
    <meta name='description' content='Retrieve a Wikipedia page from SBN authority control codes.' />
    <meta name='keywords' content='Wikipedia, search, VIAF, SBN, authority control' />
    <meta name="copyright" content="Cristian Consonni">

    <!-- Dublin Core Metadata -->
    <meta name="DC.identifier" content="" />
    <meta name="DC.creator" lang="en" content="Cristian Consonni">
    <meta name="DC.date.created" lang="en" content="2013-10-29">
    <meta name="DC.date.modified" lang="en" content="2013-10-29">
    <meta name="DC.format" lang="en" content="text/html">
    <meta name="DC.language" content="en">

    <!-- Open Graph Metadata -->
    <meta property="og:site_name" content="gmtpun.org">
    <meta property="og:title" content="SBN Toolkit">
    <meta property="og:description" content="Retrieve a Wikipedia page from SBN authority control codes.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="">

    <!-- Navigation -->
    <link rel="home" href="/">

    <!-- Icons -->
    <link rel="shortcut icon" href="/favicon.ico" type="image/png" />
 
    <!-- CSS -->
    <link rel="stylesheet" href="/sbnt/css/style.css">
    <link rel="stylesheet" href="/sbnt/css/sbntoolkit.css">

    <!-- JS -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    <!-- <script type="text/javascript" src="/sbnt/js/paginate.js"></script> -->
</head>

<body>

    <div id="container">
        <h1>Lista di item con codice VIAF, senza codice SBN in Wikipedia in Italiano</h1>

        tot_pages: {{tot_pages}}
        active_page: {{active_page}}

        <div class="pager">
            %for pagenum in xrange(1,tot_pages+1):
                <a href="?p={{pagenum}}">
                %if active_page == pagenum: 
                    <span class="page-number active">{{pagenum}}</span></a>
                %else:
                    <span class="page-number">{{pagenum}}</span>
                %end
                </a>
            %end
        </div>
        <table class="paginated" border="1">
            <thead>
                <tr>
                    <th scope="col" style="width: 10%;">codice VIAF</th>
                    <th scope="col" style="width: 10%;">ID pagina it.wiki</th>  
                    <th scope="col" style="width: 10%;">Item Wikidata</th> 
                    <th scope="col" style="width: 30%;">Titolo pagina it.wiki</th>
                    <th scope="col" style="width: 10%;">ID wikidata</th>
                    <th scope="col" style="width: 10%;">ID collegato</th>
                </tr>
            </thead>

            <tbody>
              %for item in items:
                <tr>
                %for v in item:
                    <td>{{!v}}</td>    
                %end
                </tr>
              %end
            </tbody>
        </table>
    </div>

</body>
</html>
