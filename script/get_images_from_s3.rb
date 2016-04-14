#!/usr/bin/env ruby

require 'pry'
require 'rest_client'
require 'parallel'
require 'aws-sdk'
require 'json'
require 'logger'
require 'ruby-progressbar'

bar = ProgressBar.create

def get_images_to_download
  images = JSON.parse(File.read('data/images.json'))

  images.flat_map do |k, v|
    v.flat_map do |item|
      item.map do |type, url|
        url =~ /.+\/([^\/]+)$/
        "#{type}/#{k}/#{$1}"
      end
    end
  end
end

images = get_images_to_download
size = images.size
batch = 50000
images.reverse.each_slice(batch).with_index do |a, i|
  puts "Done %0.1f%" % (i * 100.0 * batch / size)
  Parallel.each(a, in_processes: 50, progress: "Importing") do |image|
    @images_bucket ||= Aws::S3::Bucket.new('offerup-images', Aws::S3::Client.new)

    image =~ /^(.+)\/([^\/]+)$/
    path = "data/all_images/#{$1}"
    full_path = "data/all_images/#{image}"
    unless File.exist?(full_path)
      FileUtils.mkdir_p path
      begin
        @images_bucket.object(image).get(response_target: full_path)
      rescue => e
        puts "ERROR for url '#{image}'!!! #{e.message}"
      end
    end
  end
end
