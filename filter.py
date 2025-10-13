def get_by_user_input(craft_data):
    categories = ['3D Printing', 'Arduino', 'Art', 'Boats', 'Books & Journals', 
                'Cardboard', 'Cards', 'Christmas', 'Clay', 'Cleaning', 'Clocks', 'Costumes & Cosplay', 
                'Digital Graphics', 'Duct Tape', 'Embroidery', 'Fashion', 'Felt', 'Fiber Arts', 'Furniture', 'Gift Wrapping', 
                'Halloween', 'Holidays', 'Home Improvement', 'Jewelry', 'Kids', 'Knitting & Crochet', 'Knots', 'Launchers', 
                'Leather', 'Life Hacks', 'Mason Jars', 'Math', 'Metalworking', 'Molds & Casting', 'Music', 'No-Sew', 'Paper', 
                'Parties & Weddings', 'Photography', 'Printmaking', 'Relationships', 'Reuse', 'Science', 'Sewing', 'Soapmaking', 
                'Speakers', 'Tools', 'Toys & Games', 'Wallets', 'Water', 'Wearables', 'Woodworking']

    print("Available Craft Categories:")
    print(categories)

    print("Choose a Category, or press Enter to include all")
    subcategory = input("Category: ")
    if subcategory == "":
        subcategory = None

    print("How many projects do you want to see?")
    number_of_results_input = input("Number (1-20): ")
    number_of_results = int(number_of_results_input)

    choice = input("Enter 1 for most viewed or 2 for most favorited: ")
    if choice == "1":
        sort_by_favorite = False
    else:
        sort_by_favorite = True

    if sort_by_favorite:
        sort_category = "Favorites"
    else:
        sort_category = "Views"

    if subcategory is not None:
        filtered_data = craft_data[craft_data['Subcategory'] == subcategory]
        top_viewed = filtered_data.nlargest(number_of_results, sort_category)
    else:
        top_viewed = craft_data.nlargest(number_of_results, sort_category)
    return top_viewed