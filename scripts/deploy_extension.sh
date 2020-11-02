echo "Extension layer"
python -W ignore setup.py --quiet bdist_wheel  # create .egg-info
pushd src > /dev/null || exit
echo "-create directories to zip"
echo "--extension"
mkdir extensions
cp ../scripts/logs extensions/
echo "--shipper"
mkdir extension-python-modules
cp -R lambda_log_shipper.egg-info extension-python-modules/
cp -R lambda_log_shipper extension-python-modules/
echo "--python runtime"
aws s3 cp --quiet s3://lumigo-runtimes/python/lean-python-runtime-37.zip runtime.zip
unzip -q runtime.zip
echo "--special temp file"
touch preview-extensions-ggqizro707
echo "-zipping"
zip -qr "extensions.zip" "extensions" "extension-python-modules" "python-runtime" "preview-extensions-ggqizro707"
echo "-publish"
version=$(aws lambda publish-layer-version --layer-name "logs-extension" --zip-file fileb://extensions.zip --region "us-east-1" | jq -r '.LayerVersionArn')
rm -rf extensions extension-python-modules extensions.zip runtime.zip python-runtime __MACOSX
popd > /dev/null || exit

echo "\nDone.\n"
