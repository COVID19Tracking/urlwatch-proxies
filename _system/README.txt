service setup:

    sudo cp flaskapp.service /etc/systemd/system/flaskapp.service
    sudo systemctl daemon-reload
    sudo systemctl start flaskapp
    sudo systemctl status flaskapp

nginx setup:

    sudo cp flaskapp.site /etc/nginx/sites-available/flaskapp
    sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled
    sudo systemctl restart nginx
    sudo systemctl status nginx
    sudo ufw allow 'Nginx Full'