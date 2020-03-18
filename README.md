# urlwatch-proxies

A flask website that provides several services in support of the data pipeline

Currently hosted at http://covid19-api.exemplartech.com/ but we plan to move it
to  data-archive.covidtracking.com.

## Endpoints

### Cache

    A simple cache for storing results.  The intended use is for publishing the
    results of one-off scraping processes without to setup a web server or get
    S3 data keys.

    The cache is effectively a single directory that can write to use POST.

    * GET /cache - http://covid19-api.exemplartech.com/cache?full=1

    List the contents of the cache (JSON).
    If full is set, then it includes the meta-data.
    Otherwise it just includes the names.

    * GET /cache/<xid> - http://covid19-api.exemplartech.com/cache/test_content.html

    Read the content of a cached item.
    
    * POST /cache/<xid>?owner=<owner>

    Write the post body to a cached item, creating a new one if it is missing.
    If it already exists, the owner provided must match value it was posted with. 

    * DELETE /cache/<xid>?owner=<owner>

    Delete an item from the cache.

    * GET /cache/meta/<xid> - http://covid19-api.exemplartech.com/cache/meta/test_content.html

    Get the meta-data for an item in the cache (JSON).
    
    > Warning -- This is not a secure storage location!!!
    > It is trival for someone to discover the owner of a file and overwrite it.
    > If it is abused, I will lock it down. - Josh


### MetaData for Tracking Project

    Access meta-data for the tracking project from various sources.  All data is
    pulled dynamically when you request it so it should never be out of sync.

    We currently have two sources for configuration information:
    > urlwatch: https://github.com/COVID19Tracking/covid-tracking/blob/master/urls.yaml
    > google: https://docs.google.com/spreadsheets/d/18oVRrHj3c183mHmq3m89_163yuYltLNlOmPerQ18E8w/htmlview?sle=true

    * GET /config/urlwatch/urls.yaml - http://covid19-api.exemplartech.com/config/urlwatch/urls.yaml
   
    Get the raw configuration file for urlwatch

    * GET /config/urlwatch/urls.json - http://covid19-api.exemplartech.com/config/urlwatch/urls.json

    Get the raw configuration file for urlwatch as JSON

    * GET /config/google - http://covid19-api.exemplartech.com/config/google/

    Get the tabs from the google worksheet.

    * GET /config/google/states - http://covid19-api.exemplartech.com/config/google/states

    Get the States tab from the google worksheet.

    * GET /config/google/current - http://covid19-api.exemplartech.com/config/google/current

    Get the 'States current' tab from the google worksheet.

###    GitHub Data View

    The data pipeline stores results in GitHub but there is not a clean way to view the underlying result.
    These API calls let you view the data.  It has data back to 3/15 but I do not currently provide a way
    to look at history without checking out the repo directly. 

    * GET /github-data/<path>

    Get an item from the gitub repo storing the data.

    > The source repo is currently at https://github.com/joshuaellinger/corona19-data-archive but I
    > am going to move it under the tracker project soon. - Josh

### Data Pipeline File Structure

    The data pipeline currently runs off of the state tab of the Google worksheet.  Eventually, we will create
    a unified view between states and urlwatch that has a combined list of files but, for now, they serve
    different purposes.

    The pipeline maintains three parallel sets of tiles
        1. **raw_** - the raw html content
        2. **clean** - the content after removing all script and styling, as well as items that vary with each request.
        3. **extract** - the *interesting* content, reorganized to highlight the data.

    The files look ugly because we don't take all the auxillary files or fix the relative links.        

    The pipeline creates an index file for human consumption at:

    > http://covid19-api.exemplartech.com/github-data/extract/index.thml

    The index file shows information like:
        1. status from last run
        2. time of last update
        3. source URL

    It links to specific results such as:
    
    > http://covid19-api.exemplartech.com/github-data/extract/ca.html

    The same data is available in different formats at:

    > http://covid19-api.exemplartech.com/github-data/raw/change_list.txt
    > http://covid19-api.exemplartech.com/github-data/raw/change_list.json



###    Proxy [Obsolete] 

    The endpoints implement a proxy that cleans up an HTML file.  However, the approach doesn't work well
    in practice so it has been abandonned.  The data pipeline performs the same task in a better fashion.

    * GET /proxy/

    Get the data but regularize it by string out most items that change on every request

    * GET /proxy-raw/

    Get the raw data without any cleanup



## Hosting

hosted on Digital Ocean by @joshuaellinger

[Configuration Tutorial](https://pythonforundergradengineers.com/flask-app-on-digital-ocean.html#set-up-a-new-digital-ocean-droplet)
    
