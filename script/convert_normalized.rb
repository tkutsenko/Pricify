#!/usr/bin/env ruby

require 'json'

items = JSON.parse(File.read('./normalized/items_k.json'))
owners = JSON.parse(File.read('./normalized/owners_k.json'))

File.write('./normalized/items.json', items.values.to_json)
File.write('./normalized/owners.json', owners.values.to_json)
