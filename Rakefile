file "build/out.epub" => FileList["rst/Prologue_Prologue.rst"] do
	mkdir_p "build"
	sh 'echo "Practical Guide to Evil.\n========================\n\practicalguidetoevil.wordpress.com\n------------------------\n" > rst/0.0_Title.rst'
	sh "txt2epub build/out.epub rst/*.rst --title='Practical Guide to Evil' --creator=practicalguidetoevil.wordpress.com"
end


#mirror_fname = "mirror/category/stories-arcs-1-10/arc-1-gestation/1-01/index.html"
mirror_fname = "mirror/2017/09/04/chapter-28-gambits/index.html"

file mirror_fname do
	Dir.chdir("WPepub") do
		sh "python scrape.py"
	end
end

file "rst/Prologue_Prologue.rst" => [mirror_fname] do
	Dir.chdir("WPepub") do
		sh "python convert.py"
	end
end

task :compile => ["build/out.epub"]

task :default => [:compile]
