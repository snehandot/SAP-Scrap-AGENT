import csv

def get_user_inputs():
    inputs = []
    while True:
        website_link = input("Name of Website that is chosen: ")
        if website_link.lower() == 'exit':
            return inputs, True
        elif website_link.lower() == 'next':
            return inputs, False
        inputs.append(website_link)
        
        while True:
            user_input = input("Enter button (type 'next' for next website, 'exit' to finish): ")
            if user_input.lower() == 'exit':
                return inputs, True
            elif user_input.lower() == 'next':
                return inputs, False
            inputs.append(user_input)

def save_to_csv(data, filename='user_inputs.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if data:
            writer.writerow(data)

def main():
    print("This program will continuously ask for user input.")
    print("Type 'next' to move to the next row, 'exit' to finish.")
    while True:
        inputs, should_exit = get_user_inputs()
        if inputs:
            save_to_csv(inputs)
        if should_exit:
            print("Exiting the program.")
            break

if __name__ == '__main__':
    main()

