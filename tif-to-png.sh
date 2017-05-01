convert_tif_in_dir () {
  rm $1/*.png
  for i in $1/*;
  do
    sips -s format jpeg $i --out $i.jpeg;
  done
}


for d in ./app/static/images/*''
do
  # echo "$d"
  convert_tif_in_dir $d;
done