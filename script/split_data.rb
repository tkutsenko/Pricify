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
