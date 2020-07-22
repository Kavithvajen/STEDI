yes = ("Y", "y", "yes", "Yes", "YES")
no = ("N", "n", "no", "No", "NO")

def main():
    option = input("\nYes or No [Y/N]: ")
    if option in yes:
        print("Yes")
    elif option in no:
        print("No")
    else:
        print("Else!")

if __name__ == "__main__":
    main()
