# sunvox.audio

Backend for the [sunvox.audio](https://sunvox.audio/) website.

License: MIT

We encourage you to join in on the fun!

## Branding

This is not intended to be used outside of being hosted at
[sunvox.audio](https://sunvox.audio/)
or beta/staging sites maintained by its developers.

If you fork this with the intention of making a new site,
please be sure to change the name to something other than "sunvox.audio".

Thanks!

## Initial setup

First, install the latest version of docker.

Then, run this to bring up your stack:

    $ docker compose up

When everything is running you should be able to visit these sites:

* [Django server at http://localhost:8000](http://localhost:8000)
* [Mailhog server at http://localhost:8025](http://localhost:8025)

## Basic Commands

### Setting Up Your Users

To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your [Mailhog server](http://localhost:8025) to see a simulated email verification message. Click the link. Now the user's email should be verified and ready to go.

To create an **superuser account**, use this command:

    $ ./django.sh ./manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Running tests with py.test

    $ ./django.sh pytest
