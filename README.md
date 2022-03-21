# MatplotCLI

## Create matplotlib visualizations from the command-line

MatplotCLI is a simple utility to quickly create plots from the command-line, leveraging [Matplotlib](https://github.com/matplotlib/matplotlib). 

```sh
plt "scatter(x,y,5,alpha=0.05); axis('scaled')" < sample.json
```

![](https://github.com/dcmoura/matplotcli/raw/main/img/scatter_sample.png)

```sh
plt "hist(x,30)" < sample.json
```

![](https://github.com/dcmoura/matplotcli/raw/main/img/hist_sample.png)


The format of the input data format is [JSON lines](https://jsonlines.org), where each line is a valid JSON object. Look at the recipes section to learn how to handle other formats like CSV.

MatplotCLI executes python code (passed as argument) where some handy imports are already done (e.g. `from matplotlib.pyplot import *`) and where the input JSON data is already parsed and available in variables, making plotting easy. Please refer to `matplotlib.pyplot`'s [reference](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html#module-matplotlib.pyplot) and [tutorial](https://matplotlib.org/stable/tutorials/introductory/pyplot.html) for comprehensive documentation about the plotting commands. 

Data from the input JSON is made available in the following way. Given the input `myfile.json`:

```json
{"a": 1, "b": 2}
{"a": 10, "b": 20}
{"a": 30, "c$d": 40}
```

The following variables are made available:

```python
data = {
    "a": [1, 10, 30],
    "b": [2, 20, None],
    "c_d": [None, None, 40]
}

a = [1, 10, 30]
b = [2, 20, None]
c_d = [None, None, 40]

col_names = ("a", "b", "c_d")
```

So, for a scatter plot `a vs b`, you could simply do:

```
plt "scatter(a,b); title('a vs b')" < myfile.json
```

Notice that the names of JSON properties are converted into valid Python identifiers whenever they are not (e.g. `c$d` was converted into `c_d`).

## Execution flow

1. Import matplotlib and other libs;
2. Read JSON data from standard input;
3. Execute user code;
4. Show the plot.

All steps (except step 3) can be skipped through command-line options.


## Installation

The easiest way to install MatplotCLI is from `pip`:

```sh
pip install matplotcli
```
   


## Recipes and Examples

### Plotting from a json array

[jq](https://stedolan.github.io/jq/) is a very handy utility whenever we need to handle different JSON flavors. The `-c` option guarantees one JSON object per line in the output. 

```sh
echo '[
    {"a":0, "b":1},
    {"a":1, "b":0},
    {"a":3, "b":3}
    ]' | 
jq -c .[] | 
plt "plot(a,b)"
```


### Plotting from a csv

[SPyQL](https://github.com/dcmoura/spyql) is a data querying tool that allows running SQL queries with Python expressions on top of different data formats. Here, SPyQL is reading a CSV file, automatically detecting if there's an header row, the dialect and the data type of each column, and converting the output to JSON lines before handing over to MatplotCLI.


```sh
cat my.csv | spyql "SELECT * FROM csv TO json" | plt "plot(x,y)"
```

### Plotting from a yaml/xml/toml

[yq](https://kislyuk.github.io/yq/#) converts yaml, xml and toml files to json, allowing to easily plot any of these with MatplotCLI.

```sh
cat file.yaml | yq -c | plt "plot(x,y)"
```
```sh
cat file.xml | xq -c | plt "plot(x,y)"
```
```sh
cat file.toml | tomlq -c | plt "plot(x,y)"
```

### Plotting from a parquet file

 `parquet-tools` allows dumping a parquet file to JSON format.  `jq -c` makes sure that the output has 1 JSON object per line before handing over to MatplotCLI.

```sh
parquet-tools cat --json my.parquet | jq -c | plt "plot(x,y)"
```

### Plotting from a database

Databases CLIs typically have an option to output query results in CSV format (e.g. `psql --csv -c query`  for PostgreSQL, `sqlite3 -csv -header file.db query` for SQLite). 

Here we are visualizing how much space each namespace is taking in a PostgreSQL database.
[SPyQL](https://github.com/dcmoura/spyql) converts CSV output from the psql client to JSON lines, and makes sure there are no more than 10 items, aggregating the smaller namespaces in an `All others` category.
Finally, MatplotCLI makes a pie chart based on the space each namespace is taking. 

```sh
psql -U myuser mydb --csv  -c '
    SELECT 
        N.nspname,
        sum(pg_relation_size(C.oid))*1e-6 AS size_mb
    FROM pg_class C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    GROUP BY 1 
    ORDER BY 2 DESC' | 
spyql "
    SELECT 
        nspname if row_number < 10 else 'All others' as name, 
        sum_agg(size_mb) AS size_mb 
    FROM csv 
    GROUP BY 1 
    TO json" | 
plt "
nice_labels = ['{0}\n{1:,.0f} MB'.format(n,s) for n,s in zip(name,size_mb)];
pie(size_mb, labels=nice_labels, autopct='%1.f%%', pctdistance=0.8, rotatelabels=True)"
```

![](https://github.com/dcmoura/matplotcli/raw/main/img/pie_pg.png)


### Plotting a function 

Disabling reading from stdin and generating the output using `numpy`.

```sh
plt --no-input "
x = np.linspace(-1,1,2000); 
y = x*np.sin(1/x); 
plot(x,y); 
axis('scaled'); 
grid(True)"
```
![](https://github.com/dcmoura/matplotcli/raw/main/img/plot_func.png)


### Saving the plot to an image

Saving the output without showing the interactive window.

```sh
cat sample.json | 
plt --no-show "
hist(x,30); 
savefig('myimage.png', bbox_inches='tight')"
```

### Plot of the global temperature

Here's a complete pipeline from getting the data to transforming and plotting it:

1. Downloading a CSV file with `curl`; 
2. Skipping the first row with `sed`;
3. Grabbing the year column and 12 columns with monthly temperatures to an array and converting to JSON lines format using [SPyQL](https://github.com/dcmoura/spyql);
4. Exploding the monthly array with SPyQL (resulting in 12 rows per year) while removing invalid monthly measurements;
5. Plotting with MatplotCLI  .

```sh
curl https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv |
sed 1d | 
spyql "
  SELECT Year, cols[1:13] AS temps 
  FROM csv 
  TO json" | 
spyql "
  SELECT 
    json->Year + ((row_number-1)%12)/12 AS year, 
    json->temps AS temp 
  FROM json 
  EXPLODE json->temps 
  WHERE json->temps is not Null 
  TO json" | 
plt "
scatter(year, temp, 2, temp); 
xlabel('Year'); 
ylabel('Temperature anomaly w.r.t. 1951-80 (ºC)'); 
title('Global surface temperature (land and ocean)')"
```

![](https://github.com/dcmoura/matplotcli/raw/main/img/scatter_temperature.png)