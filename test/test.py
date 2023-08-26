from mongosanitizer.sanitizer import sanitize

testobjekt={'$gte':{'test':'testvalue'}}

test_sanitized=sanitize(testobjekt)

print(test_sanitized)