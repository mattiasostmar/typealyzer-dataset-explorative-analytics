# SETUP

Create a conda environment with py3.5, spacy, jupyter, matplotlib, seaborn and pandas

    $ conda create -n memeticscience python=3.5 spacy jupyter pandas matplotlib seaborn plotly scikit-learn

Pip install tldextract, used for extracting domains from URLs in cleaning process
    
    $ pip install tldextract


We also need [langdetect](https://github.com/Mimino666/langdetect), a port of Googles language-detection library
    
    $ pip install langdetect

Clone this repository

    $ git clone git@gitlab.com:memetic-science/Jung-Myers-tagger.git


Download the multi-language spacy model

    $ python -m spacy download xx


