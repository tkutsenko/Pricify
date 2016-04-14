#!/usr/bin/env ruby

require 'pry'
require 'rest_client'
require 'parallel'
require 'aws-sdk'
require 'json'
require 'logger'

def object_exists?(key, bucket)
  bucket.object(key).get
  true
rescue Aws::S3::Errors::NoSuchKey
  false
end

@s3 = Aws::S3::Client.new
@src_bucket = Aws::S3::Bucket.new('offerup-data', @s3)

items = JSON.parse(@src_bucket.object('items.json').get.data.body.read)
size = items.size
puts "Processing #{size} items"
batch = 0
items.each_slice(10000) do |slice|
  batch += 1
  Parallel.each_with_index(slice, in_processes: 50, progress: "Importing items batch #{batch}/#{size/10000}") do |item, i|
    @dst_bucket ||= Aws::S3::Bucket.new('offerup-data-split1', Aws::S3::Client.new)
    begin
      key = "items1/#{item['id']}.json"
      puts "Key #{key} exists" if object_exists?(key, @dst_bucket)
      @dst_bucket.put_object(key: key, body: item.to_json)
    rescue => e
      puts "Error: #{e.message}"
    end
  end
end
items = nil
#
# owners = JSON.parse(@src_bucket.object('owners.json').get.data.body.read)
# size = owners.size
# Parallel.each_with_index(owners, in_processes: 50) do |owner, i|
# # owners.each_with_index do |owner, i|
#   @dst_bucket ||= Aws::S3::Bucket.new('offerup-data-split', Aws::S3::Client.new)
#   @processed = 0 if @processed.nil?
#   @processed += 1
#   if i % 1000 == 0
#     puts "Processed #{i} owners, #{size - i} left"
#   end
#
#   @dst_bucket.put_object(key: "owners/#{owner['id']}.json", body: owner.to_json)
#   nil
# end
# owners = nil
#
# images = JSON.parse(@src_bucket.object('images.json').get.data.body.read)
# size = images.size
# # Parallel.each_with_index(images, in_processes: 50) do |k, images, i|
# images.each_with_index do |a, i|
#   k = a.first
#   images = a.last
#   @dst_bucket ||= Aws::S3::Bucket.new('offerup-data-split', Aws::S3::Client.new)
#   @processed = 0 if @processed.nil?
#   @processed += 1
#   if i % 1000 == 0
#     puts "Processed #{i} images, #{size - i} left"
#   end
#
#   @dst_bucket.put_object(key: "images/#{k}.json", body: images.to_json)
#   nil
# end
# images = nil
