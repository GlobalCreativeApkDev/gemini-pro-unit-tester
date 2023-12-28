"""
This file contains code for the application "Gemini Pro Unit Tester".
Author: GlobalCreativeApkDev
"""


# Importing necessary libraries


import google.generativeai as gemini
import sys
import os
from dotenv import load_dotenv
from mpmath import mp, mpf

mp.pretty = True


# Creating static functions to be used in this application.


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating main function used to run the application.


def main() -> int:
    """
    This main function is used to run the application.
    :return: an integer
    """

    load_dotenv()
    gemini.configure(api_key=os.environ['GEMINI_API_KEY'])

    # Asking user input values for generation config
    temperature: str = input("Please enter temperature (0 - 1): ")
    while not is_number(temperature) or float(temperature) < 0 or float(temperature) > 1:
        temperature = input("Sorry, invalid input! Please re-enter temperature (0 - 1): ")

    float_temperature: float = float(temperature)

    top_p: str = input("Please enter Top P (0 - 1): ")
    while not is_number(top_p) or float(top_p) < 0 or float(top_p) > 1:
        top_p = input("Sorry, invalid input! Please re-enter Top P (0 - 1): ")

    float_top_p: float = float(top_p)

    top_k: str = input("Please enter Top K (at least 1): ")
    while not is_number(top_k) or int(top_k) < 1:
        top_k = input("Sorry, invalid input! Please re-enter Top K (at least 1): ")

    float_top_k: int = int(top_k)

    max_output_tokens: str = input("Please enter maximum input tokens (at least 1): ")
    while not is_number(max_output_tokens) or int(max_output_tokens) < 1:
        max_output_tokens = input("Sorry, invalid input! Please re-enter maximum input tokens (at least 1): ")

    int_max_output_tokens: int = int(max_output_tokens)

    # Set up the model
    generation_config = {
        "temperature": float_temperature,
        "top_p": float_top_p,
        "top_k": float_top_k,
        "max_output_tokens": int_max_output_tokens,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = gemini.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    while True:
        clear()
        language: str = input("What programming language do you want to run unit files in? ")
        convo.send_message("Is " + str(language) + " a programming language (one word response only)?")
        language_check_answer: str = str(convo.last.text).upper()
        while language_check_answer != "YES":
            language: str = input("Sorry, invalid input! What programming language do you want to run unit files in? ")
            convo.send_message("Is " + str(language) + " a programming language (one word response only)?")
            language_check_answer = str(convo.last.text).upper()

        convo = model.start_chat(history=[
        ])
        file_to_test: str = input("Please enter the path of the " + str(language).lower().capitalize()
                                  + " file you want to test: ")
        convo.send_message("Is " + str(file_to_test) + " a " + str(language).lower().capitalize() +
                           " file (one word response only)?")
        answer: str = str(convo.last.text).upper()
        while answer != "YES":
            file_to_test: str = input(
                "Sorry, invalid input! "
                "Please enter the " + str(language).lower().capitalize() + " file you want to test: ")
            convo.send_message("Is " + str(file_to_test) + " a " + str(language).lower().capitalize() +
                               " file (one word response only)?")
            answer = str(convo.last.text).upper()

        file = open(str(file_to_test), "r")
        file_contents: str = str(file.read())
        file.close()

        convo = model.start_chat(history=[
        ])
        convo.send_message("Can you generate unit tests for the following " + str(language).lower().capitalize() +
                           " file please import the file " + str(file_to_test)
                           + " and the unit test modules too, assuming the newly created unit "
                           "tests file is in the same directory as the following " + str(language).lower().capitalize()
                           + " file, including only the " + str(language).lower().capitalize()
                           + " code in your response)?\n\n" + str(file_contents))
        unit_tests_code_response: str = str(convo.last.text)
        unit_tests_code: str = '\n'.join(unit_tests_code_response.split('\n')[1:-1])
        convo = model.start_chat(history=[
        ])
        convo.send_message("What is the extension of a " + str(language).lower().capitalize()
                           + " file (please include the dot, one word response only)?")
        unit_test_file_extension: str = str(convo.last.text)
        unit_test_file_name: str = str(file_to_test.split(".")[0]) + "_Tests"
        unit_test_file_path: str = str(unit_test_file_name) + str(unit_test_file_extension)

        # Writing test code to unit files file
        test_file = open(str(unit_test_file_path), "w")
        test_file.write(unit_tests_code)
        test_file.close()

        # Generating command to run the unit test file.
        convo = model.start_chat(history=[
        ])
        convo.send_message("What is the command to run the unit test for the file "
                           + str(unit_test_file_path) + " (only include commands in your response)?")
        run_unit_test_command: str = str(convo.last.text)
        print("Executing command: " + str(run_unit_test_command))
        os.system(run_unit_test_command)

        # Checking whether the user wants to continue unit testing or not.
        print("Enter 'Y' for yes.")
        print("Enter anything else for no.")
        continue_testing: str = input("Do you want to continue running unit files? ")
        if continue_testing != "Y":
            return 0


if __name__ == '__main__':
    main()
