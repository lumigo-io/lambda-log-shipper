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
aws s3 cp --quiet s3://lumigo-runtimes/python/python-runtime-37.zip runtime.zip
unzip -q runtime.zip
mv python python-runtime

echo "--special temp file"
touch preview-extensions-ggqizro707


echo "-zipping"
zip -qr "extensions.zip" "extensions" "extension-python-modules" "python-runtime" "preview-extensions-ggqizro707"


echo "-publish"
enc_location=../common-resources/encrypted_files/credentials_production.enc
mkdir -p ~/.aws
echo ${KEY} | gpg --batch -d --passphrase-fd 0 ${enc_location} > ~/.aws/credentials
regions=("ap-northeast-1" "ap-northeast-2" "ap-south-1" "ap-southeast-1" "ap-southeast-2" "ca-central-1" "eu-central-1" "eu-north-1" "eu-west-1" "eu-west-2" "eu-west-3" "sa-east-1" "us-east-1" "us-east-2" "us-west-1" "us-west-2" "ap-east-1" "me-south-1")
layer_name="lambda-log-shipper"
for region in "${regions[@]}"; do
    version=$(aws lambda publish-layer-version --layer-name "${layer_name}" --description "No-code to ship your logs" --zip-file fileb://extensions.zip --region ${region} --cli-connect-timeout 6000 | jq -r '.Version')
    aws lambda add-layer-version-permission --layer-name "${layer_name}" --statement-id engineering-org --principal "*" --action lambda:GetLayerVersion --version-number ${version} --region ${region} > /dev/null
    echo "published layer version: ${version} in region: ${region}"
done
rm -rf extensions extension-python-modules extensions.zip runtime.zip python-runtime __MACOSX preview-extensions-ggqizro707
popd > /dev/null || exit


echo "-update README"
sed -i -E "s/\(arn:aws:lambda:<region>:114300393969:layer:${layer_name}:\)[0-9]*/\1${version}/" README.md
rm README.md-E


echo
echo "Done! Latest version: ${version}"
echo
