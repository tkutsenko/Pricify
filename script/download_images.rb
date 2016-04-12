#!/usr/bin/env ruby

require 'pry'
require 'rest_client'
require 'parallel'
require 'aws-sdk'
require 'json'
require 'logger'

@s3 = Aws::S3::Client.new
@images_bucket = Aws::S3::Bucket.new('offerup-images', @s3)

def object_exists?(key, bucket)
  bucket.object(key).get
  true
rescue Aws::S3::Errors::NoSuchKey
  false
end

def get_images_to_download
  images = JSON.parse(Aws::S3::Bucket.new('offerup-data', @s3).object('images.json').get.data.body.read)

  images.flat_map do |k, v|
    v.map { |item| { id: k, images: item} }
  end
end

to_download = get_images_to_download

Parallel.each_with_index(to_download, in_processes: 10) do |images, i|
  @images_bucket ||= Aws::S3::Bucket.new('offerup-images', Aws::S3::Client.new)

  @logger ||= Logger.new(File.open("logs/downloader_info#{i}.log", 'w'))
  @errors_log ||=  Logger.new(File.open("logs/downloader_errors#{i}.log", 'w'))

  @processed ||= 0
  @processed += 1
  if i == 0 && @processed % 100 == 0
    puts "Processed #{@processed * 10} items"
  end

  errors = 0
  errored_types = []
  ['full', 'list', 'detail'].each do |type|
    begin
      url = images[:images][type]
      url =~ /.+\/([^\/]+)$/
      key = "#{type}/#{images[:id]}/#{$1}"
      next if object_exists?(key, @images_bucket)
      resp = RestClient.get(url)
      content_type = resp.headers[:content_type]
      @images_bucket.put_object(key: key, body: resp.body, content_type: content_type)
    rescue => e
      errored_types << type
      errors += 1
      @errors_log.warn("Error #{e.class.name}: #{e.message}")
    end
    if (errors > 0)
      @logger.warn("#{images[:id]}: #{errors} errors for types: #{errored_types.join(',')}")
    else
      @logger.info("#{images[:id]}: downloaded")
    end
  end
end
