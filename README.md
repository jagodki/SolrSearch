# SolrSearch
SolrSearch is a QGIS-plugin to integrate an Apache Solr installation into the locator filter:
<br><img width="310" alt="Bildschirmfoto 2021-08-29 um 19 50 58" src="https://user-images.githubusercontent.com/23242936/131260351-03aa225d-0fce-4e63-8df2-8237f3c72f7f.png"><br>
This plugin allows QGIS to connect to a search platform realised by Apache Solr. Depending on the data in the search platform, the user has the option of a full text search with a spatial component to change the map position according to the selected search result.

## Usage
Just type in the search string and a request will be send to the configured Apache Solr.
The search results will be grouped by their cores. A double click will zoom the map canvas on the search result and a red polygon around the result will be displayed.
This red polygon will disappear, when the search string will be adjusted or removed.

## Installation
The plugin itself is available via the <a href="https://plugins.qgis.org">QGIS Plugin repository</a> and directly within QGIS from the Plugin Manager.
An addtional installation of Apache Solr is mandatory for using the plugin.

## Configuration
The plugin will be shipped with a configuration file in json format named settings.json:
<br><img width="203" alt="Bildschirmfoto 2021-08-29 um 20 00 51" src="https://user-images.githubusercontent.com/23242936/131260683-61344bd6-f4bb-4eff-81d8-b6bac9b36920.png"><br>
The parameters for working with an Apache Solr installation has to be stored in this file.

### Path to settings.json
At startup the plugin looks for QgsSettings to get the path to the settings-file. If this QgsSettings are not set, the plugin looks in its directory for this file.
```python
#read the settings
settings_path = QgsSettings().value("SolrSearch/settings_path", str(pathlib.Path(__file__).parent.resolve()) + "/settings.json")
self.settings = SolrSearchSettings(settings_path)
```
To run this plugin in an production environment, make sure that each user/profile has this QgsSettings set.

### settings.json
The shipped settings file is just an example and has to be edited before using it, because there is no working Apache Solr installation configured into it:
```json
{
	"prefix": "solr",
	"max_results": 10,
	"point_scale": 2500,
	"solr_cores": [
		{
			"internal_name": "core",
			"external_name": "Solr Core",
			"url": "http://localhost:8080/solr/core/select?",
			"query": {
				"query_field": "text",
				"query_prefix": "(",
				"query_suffix": ")",
				"connection": "+"
			},
			"icon_path": "",
			"result_field": "content",
			"geom_field": "geo"
		}
	]
}
```
### JSON Schema
<table>
  <tr>
    <th>parameter</th>
    <th>type</th>
    <th>explanation</th>
  </tr>
  <tr>
    <td>prefix</td>
    <td>String</td>
    <td>The prefix of this plugin in the locator search bar.</td>
  </tr>
  <tr>
    <td>max_results</td>
    <td>Integer</td>
    <td>The maximum number of search results that should be shown. This value will be used for each configured Solr Core, i.e. if two cores will be queried by this plugin, there will be 20 or less search results.</td>
  </tr>
  <tr>
    <td>point_scale</td>
    <td>Integer</td>
    <td>The number of the map scale after clicking on a search result. The plugin will zoom to the spatial information of a search result and settings this number as the map scale.</td>
  </tr>
  <tr>
    <td>solr_cores</td>
    <td>Array</td>
    <td>An array of all Solr Cores that will be queried.</td>
  </tr>
  <tr>
    <td>internal_name</td>
    <td>String</td>
    <td>The name of the Solr Core. This value will be used for the query.</td>
  </tr>
  <tr>
    <td>external_name</td>
    <td>String</td>
    <td>The name of the Solr Core that will be displayed in the locator search bar.</td>
  </tr>
  <tr>
    <td>url</td>
    <td>String</td>
    <td>The url of the Solr Core excluding any HTTP-Get-parameter.</td>
  </tr>
  <tr>
    <td>query</td>
    <td>Object</td>
    <td>An object containing additional information for creating a HTTP-Get-Request on a Solr Core.</td>
  </tr>
  <tr>
    <td>query_field</td>
    <td>String</td>
    <td>The name of the field that should be queried with the fq-parameter, could also be *.</td>
  </tr>
  <tr>
    <td>query_prefix</td>
    <td>String</td>
    <td>A prefix that will be added to the beginning of the query string.</td>
  </tr>
  <tr>
    <td>query_suffix</td>
    <td>String</td>
    <td>A suffix that will be added to the end of the query string.</td>
  </tr>
  <tr>
    <td>connection</td>
    <td>String</td>
    <td>The plugin splits all entered search strings by spaces. The value of this parameter will be used to connect the splitted string, e.g. to query multiple strings with AND or OR.</td>
  </tr>
  <tr>
    <td>icon_path</td>
    <td>String</td>
    <td>The path to a icon (png, jpg, gif, etc.) that will be displayed on front of the search results of this core. The icon has to be be located on a filesystem.</td>
  </tr>
  <tr>
    <td>result_field</td>
    <td>String</td>
    <td>The name of the json item that should be displayed as a search result in the locator search bar. The type of this field has to be string. The complete field content will be displayed.</td>
  </tr>
  <tr>
    <td>geom_field</td>
    <td>String</td>
    <td>The name of the geometry field. The Geometry has to be a Well-Known-Text (WKT) with a single geometry.</td>
  </tr>
</table>

## Apache Solr Configuration
It is mandatory to load spatial information into the Solr Cores, so that the plugin can zoom the map canvas on the spatial component of the search results. 
The spatial data has to be stored as Well-Known-Text (WKT) and with single geometries only.

## Limitations
The current version of the plugin has the following limitations:
- only one column or all via * can be queried
- the inserted search string will be splitted by spaces, all substrings will be connected via logical operators for the query
- only the logical operator AND is supported to connect search strings
- the HTTP-Get-parameters q and fq will be used for the query in one request

Following the creation of the request with core as a json object from the configuration file:
```python
#create the request url
url = (core.get("url")
    + "q="
    + core.get("query").get("query_field")
    + ":*"
    + "&fq="
    + core.get("query").get("query_field")
    + ":"
    + core.get("query").get("query_prefix")
    + "*"
    + search_string
    + "*"
    + core.get("query").get("query_suffix")
    + "&q.op=AND"
    + "&wt=json&rows="
    + str(self.settings.getMaxRows()))
```
