import boto3

# BUCKET = "att-sys-media"
# KEY_SOURCE = "david.jpg"
# KEY_TARGET = "esan.jpg"

def compare_faces( key, key_target, bucket="att-sys-media", bucket_target="att-sys-media", threshold=0, region="us-east-2"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.compare_faces(
	    SourceImage={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		TargetImage={
			"S3Object": {
				"Bucket": bucket_target,
				"Name": key_target,
			}
		},
	    SimilarityThreshold=threshold,
	)
	print("\n\n\n compare_faces response is ===>   \n\n", response)

	return  response['FaceMatches'][0]['Similarity']

def recognize(old, new):
	return compare_faces(key=old, key_target= new)


# source_face, matches = compare_faces(BUCKET, KEY_SOURCE, BUCKET, KEY_TARGET)

# print ("source face ==>  ", source_face)
# print("matches ==>", matches)
# print("\n\n")
# # the main source face
# print ("Source Face ({})".format(source_face['Confidence']))

# # one match for each target face
# for match in matches:
# 	print ("Target Face ({})".format(match['Face']['Confidence']))
# 	print ("  Similarity : {}%".format(match['Similarity']))

"""
    Expected output:
    
    Source Face (99.945602417%)
    Target Face (99.9963378906%)
      Similarity : 89.0%
"""