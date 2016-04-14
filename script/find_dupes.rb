#!/usr/bin/env ruby

require 'pry'
require 'rest_client'
require 'parallel'
require 'aws-sdk'
require 'json'
require 'logger'

@s3 = Aws::S3::Client.new
@src_bucket = Aws::S3::Bucket.new('offerup-data', @s3)

items = JSON.parse(@src_bucket.object('items.json').get.data.body.read)
items.each do |item|
  puts item if item['id'] == 77016233

end
