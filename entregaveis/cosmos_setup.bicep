targetScope = 'resourceGroup'

@minLength(3)
param accountName string
param location string = resourceGroup().location
param dbName string = 'marketpulse'
param containerName string = 'articles'

resource acct 'Microsoft.DocumentDB/databaseAccounts@2024-04-15' = {
  name: accountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    enableFreeTier: true
    capabilities: [ { name: 'EnableServerless' } ]
    locations: [
      { locationName: location, failoverPriority: 0, isZoneRedundant: false }
    ]
  }
}

resource sqldb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-04-15' = {
  name: '${acct.name}/${dbName}'
  properties: { resource: { id: dbName } }
  dependsOn: [acct]
}

resource cont 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-04-15' = {
  name: '${acct.name}/${dbName}/${containerName}'
  properties: {
    resource: {
      id: containerName
      partitionKey: { paths: ['/dt_partition'], kind: 'Hash' }
      indexingPolicy: { indexingMode: 'consistent' }
    }
  }
  dependsOn: [sqldb]
}
