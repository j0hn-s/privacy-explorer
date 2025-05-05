# Privacy Explorer
    The Privacy Explorer library lets you analyse what privacy threats may arise from combining two or more datasets. Users must provide a high-level description of the datasets they are working with from a set of pre-defined typologies, column header and data types. Privacy threats are modeled using a traffic light system coupled with a description of the types of privacy threats that are likely to arise, as well as what technologies and techniques you could consider applying to mitigate prospective privacy risks.

## User Interface
    High-level information about the datasets that the user wishes to combine are inputted into a frontend built with gov.uk-compatible scripting (HTML powered by HTMX for ease). In practice you can use this library without the UI through the CLI and/or build your own more dynamic front-end. While the front-end will likey continue to be iterated over time the pre-defined templating makes it somewhat restrictive for the timebeing.  

## Installation 
    [placeholder]: ```poetry install```

### Future Development Work 
    Aside from iterating the front-end component of the library to make the UI more dynamic and accessible, it would likely be useful to provide an API. 