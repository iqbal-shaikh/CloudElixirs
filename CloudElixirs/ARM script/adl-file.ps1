echo "this script creates an ADL and creates an empty csv file in it"
New-AzResourceGroupDeployment -ResourceGroupName abz-bigdata-projects-01 -TemplateFile /home/mohammad/adl_template.json
Import-AzureRmDataLakeStoreItem -AccountName "elixirdatalake" -Path "/home/mohammad/output.csv" -Destination "/output.csv"
Import-AzureRmDataLakeStoreItem -AccountName "elixirdatalake" -Path "/home/mohammad/output.csv" -Destination "/entities.csv" 
 
