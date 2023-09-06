import amazon_func_s3 as s3
import amazon_func_main as main

def get_data_for_php():
   objects = s3.list_objects(main.s3_uri_bucket, main.s3_client)
   str_object = ""
   for obj in objects:
      str_object += obj['Key'] + " "
   str_object = str_object[:-1]
   return str_object

if __name__ == "__main__":
   print(get_data_for_php())