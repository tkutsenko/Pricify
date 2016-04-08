#!/usr/bin/env ruby

require 'json'
items = {}
owners = {}
images = {}

Dir.glob("./scraped/*/*.json").each_with_index do |file, i|
  puts "Reading file #{i} (#{file})..."
  json = JSON.parse(File.read(file))
  json['items'].each do |item|
    owner = item.delete('owner')
    owner.delete 'get_profile'
    owners[owner['id']] = owner
    photos = item.delete('photos').map do |photo|
      result = {}
      result[:full] = photo['images']['detail_full']['url']
      result[:list] = photo['images']['list']['url']
      result[:detail] = photo['images']['detail']['url']
      result
    end
    images[item['id']] = photos
    items[item['id']] = item
  end
end

File.write('./normalized/items.json', items.values.to_json)
File.write('./normalized/owners.json', owners.values.to_json)
File.write('./normalized/images.json', images.to_json)
