# Draft the primary rule of the ETL process

!!! success

    Define the inputs, outputs, and wildcards for the rule that will run the ETL process once.

This example does not read any data from disk, so there is no `input:`. The output is a function of the location and time-period query parameters (i.e. wildcards).

??? example "`workflow/rules/datasets/weather/open_meteo.smk`"

    ```python
    {%
    include "../../../../example-answers/able_weather_01/completed/workflow/rules/datasets/weather/open_meteo.smk"
    %}
    ```
