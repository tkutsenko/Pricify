#!/usr/bin/env ruby

require 'json'
require 'parallel'
require 'fileutils'

items = JSON.parse(File.read('data/items.json'))

items_orig_size = items.size

Parallel.each_with_index(items, in_processes: 20) do |item, i|
  puts "Done #{i}/#{items_orig_size} (i * 100 / items_orig_size)" if i % 1000 == 0

  category = item['category']['name']
  copy_to = "data/images_by_category/#{category}"
  copy_from = "data/all_images/full/#{item['id']}"
  FileUtils.mkdir_p copy_to
  FileUtils.cp_r(copy_from, copy_to) if File.exists?(copy_from)
end
