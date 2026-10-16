hugo
aws s3 sync public/ s3://sv-new-horizon --delete
aws cloudfront create-invalidation --distribution-id E35L31NHLTJX3U --paths "/*"
