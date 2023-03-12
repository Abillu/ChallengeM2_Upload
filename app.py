# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
import sys
import fire
import questionary
import csv
from pathlib import Path

from qualifier.utils.fileio import load_csv

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value
from tabulate import tabulate


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    csvpath = questionary.text(
        "Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)
    if not csvpath.exists():
        sys.exit(f"Oops! Can't find this path: {csvpath}")

    return load_csv(csvpath)


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """

    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text(
        "What's your current amount of monthly debt?").ask()
    income = questionary.text("What's your total monthly income?").ask()
    loan_amount = questionary.text("What's your desired loan amount?").ask()
    home_value = questionary.text("What's your home value?").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value


"""Common header for csv file"""
header = ["Lender", "Max Loan Amount", "Max LTV",
          "Max DTI", "Min Credit Score", "Interest Rate"]


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(
        monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(
        loan_to_value_ratio, bank_data_filtered)

    print(f"Found {len(bank_data_filtered)} qualifying loans")
    print()
    print(tabulate(bank_data_filtered, header))
    print()

    return bank_data_filtered


def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    # @TODO: Complete the usability dialog for savings the CSV Files.
    # YOUR CODE HERE!

    # Set the output header
    #Check if there any qualifying loans by checking the length of the qualifying loans array. If length is zero there are no qualifying loans
    if len(qualifying_loans) > 0 :
        answer = questionary.text("Do you want to save the qualifying loans to file? (y/n)").ask()
        if answer == 'y':
            userpath = questionary.text("Enter a file path to save your csv file:").ask()                    
            csvsavepath = Path( f"{userpath}/qualifying_loans.csv")
            print()
            print("Writing the data to a CSV file...")
            print()
            print()
            print()
            # @TODO: Use the csv library and `csv.writer` to write the header row
            # Use 'with open' to open new CSV filr
            with open(csvsavepath, "w") as csvfile: 

                # Use 'csv.writer' using csv library
                csvwriter = csv.writer(csvfile, delimiter=",")

                # Use 'csv,writer' to write the header variable in the first row
                csvwriter.writerow(header)

          
            
                for qualifying_loan in qualifying_loans:

                    # Use 'csv.writer' to write the loan.values() to a rown in the CSV file
                    csvwriter.writerow([qualifying_loan[0],qualifying_loan[1],qualifying_loan[2],qualifying_loan[3],qualifying_loan[4],qualifying_loan[5]])
            
        else:
            print ("No file was saved because you opted not save file")

        
    else:
        print()
        print("There are no qualifying loans.")


def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)


if __name__ == "__main__":
    fire.Fire(run)
