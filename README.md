# Bedevere

> There are ways of telling whether an algorithm is a witch. Or a horse.

[![Build Status](https://travis-ci.org/omec/bedevere.svg?branch=master)](https://travis-ci.org/omec/bedevere)

## What's going on here?

This is the source repository for the Bedevere initiative, a community-driven approach to benchmarking content-based MIR algorithms in a transparent and sustainable way.

## Relevant Links

- B. McFee, E. J. Humphrey, and J. Urbano. [A Plan for Sustainable MIR Evaluation](https://wp.nyu.edu/ismir2016/wp-content/uploads/sites/2294/2016/07/257_Paper.pdf) ISMIR 2016. [[slides](http://bmcfee.github.io/slides/ismir2016_eval.pdf)]
- [Developer mailing list](https://groups.google.com/forum/#!forum/bedevere-dev)
- [Users mailing list](https://groups.google.com/forum/#!forum/bedevere-users)

## What is "Bedevere"?

![](https://i.ytimg.com/vi/X2xlQaimsGg/maxresdefault.jpg)

Bedevere, an alternative spelling of [Sir Bedivere](https://en.wikipedia.org/wiki/Bedivere), is the name of the character in Monty Python's [Monty Python and the Holy Grail](https://en.wikipedia.org/wiki/Monty_Python_and_the_Holy_Grail#Plot), who devises a logical test to determine whether or not a woman, brought forward by an angry mob, is in fact a witch.

Of course, and to great comic effect, there are a number of egregious errors made in the course of orchestrating this experiment, thus leading to an erroneous conclusion (that, yes, she is a witch). However, the ironic lesson of the scene is that even community-led evaluation can be misguided (especially when you _really_ want a specific outcome), but doing so in the open increases the chances that any possible ... missteps ... might be identified and corrected.


## Running the components

### Backend Server

To deploy the web backend, run the following commands in bash from within the root directory of this repository:

```
cd backend_server
pip install -t lib -r requirements/setup/requirements_dev.txt
appcfg.py -A <PROJECT_ID> -V v1 update .
```

where `<PROJECT_ID>` is a valid Google App Engine project ID. If you do not currently have one, you should [proceed here](https://console.cloud.google.com/freetrial?redirectPath=/start/appengine).

