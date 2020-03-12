# urlwatch-proxies
For proxy endpoints that normalizes content to prevent false-positive change alerts

## Endpoints

### GET /

Version Info

### GET /proxy/<path>

If you invoke the service with the path set to a state URL, it will add "https://" and
fetch the content from the requested server.

Then it will apply a set of minimal regularization changes to the parsed HTML to remove
attributes and text that change on every request.  This should make the diffs much more
reliable

### GET /proxy-raw/<path>

Returns the same content without regularization (for testing)


----

hosted on Digital Ocean by @joshuaellinger. 

[Configuration Tutorial](https://pythonforundergradengineers.com/flask-app-on-digital-ocean.html#set-up-a-new-digital-ocean-droplet)
    
