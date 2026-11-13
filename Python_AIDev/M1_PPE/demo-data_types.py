# Each assignment stores a value in a variable. Python determines its type
# from the value on the right side of the equals sign.
model_name = "SentimentBot"                      # str   -> text in quotes
parameters = 125_000_000                         # int   -> whole number; underscores aid readability
accuracy = 0.923                                 # float -> number with a decimal point
is_trained = True                                # bool  -> True or False (capitalized)
deployed_url = None                              # NoneType -> no value assigned yet
labels = ["positive", "negative", "neutral"]     # list  -> ordered and changeable
image_size = (224, 224)                          # tuple -> ordered and unchangeable
unique_languages = {"English", "Hindi", "Tamil", "English"}   # set -> unique values; order isn't guaranteed
config = {                                       # dict  -> key:value pairs
    "learning_rate": 0.001,
    "epochs": 10,
    "optimizer": "adam",
}

print(f"Model Name: {model_name} (Type: {type(model_name)})")
print(f"Parameters: {parameters} (Type: {type(parameters)})")
print(f"Accuracy: {accuracy} (Type: {type(accuracy)})")
print(f"Is Trained: {is_trained} (Type: {type(is_trained)})")
print(f"Deployed URL: {deployed_url} (Type: {type(deployed_url)})")
print(f"Labels: {labels} (Type: {type(labels)})")
print(f"Image Size: {image_size} (Type: {type(image_size)})")
print(f"Unique Languages: {unique_languages} (Type: {type(unique_languages)})")
print(f"Config: {config} (Type: {type(config)})")

# type() tells you the type of a value; print() displays it.
print(type(model_name))       # <class 'str'>
print(type(parameters))       # <class 'int'>
print(type(accuracy))         # <class 'float'>
print(type(is_trained))       # <class 'bool'>
print(type(deployed_url))     # <class 'NoneType'>
print(type(labels))           # <class 'list'>
print(type(image_size))       # <class 'tuple'>
print(type(unique_languages)) # <class 'set'>
print(type(config))           # <class 'dict'>

# Examples of using the collection types:
print(labels[0])                         # Access the first list item: positive
labels.append("mixed")                   # Lists can be changed
print(image_size[0])                     # Access a tuple item: 224
print(len(unique_languages))             # 3: the repeated "English" is kept only once
print(config["optimizer"])               # Look up a value using its dictionary key
