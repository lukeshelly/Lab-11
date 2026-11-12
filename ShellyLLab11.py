
# Name: Luke Shelly
# Class: CSEC 1437
# Assignment: Lab 11

import urllib.request
import json
import csv
import random
from html.parser import HTMLParser


class WebTextParser(HTMLParser):
    """Gets readable text from an HTML page."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tag = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip_tag = tag

    def handle_endtag(self, tag):
        if tag == self.skip_tag:
            self.skip_tag = None

    def handle_data(self, data):
        if self.skip_tag is None:
            self.text_parts.append(data)

    def get_text(self):
        return " ".join(self.text_parts)


class ShellyL_GetSearchWeb:
    """Downloads web pages and searches their words."""

    def __init__(self):
        self.SourcesDnary = {
            "Python": "https://www.python.org/",
            "NIST": "https://www.nist.gov/"
        }

        self.Custom1List = [
            ("NASA", "https://www.nasa.gov/"),
            ("NOAA", "https://www.noaa.gov/"),
            ("National Archives", "https://www.archives.gov/")
        ]

        self.Custom2List = [
            ("CISA", "https://www.cisa.gov/"),
            ("FBI", "https://www.fbi.gov/"),
            ("USA.gov", "https://www.usa.gov/")
        ]

        Custom1 = random.choice(self.Custom1List)
        Custom2 = random.choice(self.Custom2List)

        self.SourcesDnary[Custom1[0]] = Custom1[1]
        self.SourcesDnary[Custom2[0]] = Custom2[1]

        self.urls = list(self.SourcesDnary.items())
        self.search_words = []
        self.results = []

    def ask_for_urls(self):
        """Ask for website names and URLs."""
        self.urls = []

        while True:
            source = input("Enter website source name: ").strip()
            url = input("Enter website URL: ").strip()

            if source and url:
                self.urls.append((source, url))
            else:
                print("Both fields are required.")

            again = input("Enter another URL? (y/n): ")
            if again.lower() != "y":
                break

    def read_urls_from_file(self):
        """Read website names and URLs from a CSV file."""
        filename = input("Enter URL file name: ").strip()

        try:
            loaded_urls = []

            with open(filename, "r", encoding="utf-8") as file:
                reader = csv.reader(file)

                for row in reader:
                    if len(row) >= 2:
                        source = row[0].strip()
                        url = row[1].strip()

                        if source.lower() != "source":
                            if source and url:
                                loaded_urls.append((source, url))

            if loaded_urls:
                self.urls = loaded_urls
                print("URLs successfully loaded:", len(self.urls))
            else:
                print("No valid URLs found.")

        except FileNotFoundError:
            print("File was not found.")
        except Exception as error:
            print("Error reading file:", error)

    def ask_for_search_words(self):
        """Ask for up to 10 search words."""
        answer = input(
            "Enter up to 10 words separated by commas: "
        )

        self.search_words = []

        for word in answer.split(","):
            clean_word = ""

            for letter in word.strip().lower():
                if "a" <= letter <= "z":
                    clean_word += letter

            if clean_word and clean_word not in self.search_words:
                self.search_words.append(clean_word)

            if len(self.search_words) == 10:
                break

        print("Search words:", self.search_words)

    def get_web_page(self, source, url):
        """Download a webpage and return its readable text."""
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=20) as response:
                html = response.read().decode(
                    "utf-8", errors="ignore"
                )

            parser = WebTextParser()
            parser.feed(html)

            return parser.get_text()

        except Exception as error:
            print("Could not open website:", source)
            print(error)
            return None

    def make_word_lists(self, page_text):
        """Find nonalphabetic characters and create sorted unique words."""
        lower_text = page_text.lower()
        lines = lower_text.splitlines()

        non_alpha_list = []

        for line in lines:
            for character in line:
                if character < "a" or character > "z":
                    if character.isprintable():
                        if character not in non_alpha_list:
                            non_alpha_list.append(character)

        alpha_words_list = []

        for line in lines:
            word = ""

            for character in line:
                if character in non_alpha_list:
                    if word != "":
                        alpha_words_list.append(word)
                        word = ""
                else:
                    word += character

            if word != "":
                alpha_words_list.append(word)

        unique_words = []

        for word in alpha_words_list:
            if word not in unique_words:
                unique_words.append(word)

        unique_words.sort()

        return non_alpha_list, alpha_words_list, unique_words

    def run_search(self):
        """Search all selected websites."""
        self.results = []

        if not self.urls:
            print("Enter URLs or read them from a file first.")
            return

        if not self.search_words:
            print("Enter search words first.")
            return

        for source, url in self.urls:
            print("\nProcessing:", source)

            page_text = self.get_web_page(source, url)

            if page_text is None:
                continue

            non_alpha, all_words, unique_words = (
                self.make_word_lists(page_text)
            )

            word_counts = {}

            for word in self.search_words:
                word_counts[word] = all_words.count(word)

            self.results.append({
                "source": source,
                "url": url,
                "non_alpha": non_alpha,
                "unique_count": len(unique_words),
                "unique_words": unique_words,
                "word_counts": word_counts
            })

            print("Finished:", source)

        print("\nWebsite search completed.")

    def create_report(self):
        """Create a results table and website word lists."""
        lines = [
            "WEBSITE WORD SEARCH RESULTS",
            "-" * 100
        ]

        if not self.results:
            return "No results are available."

        header = f"{'Source':<22}{'Unique Words':>15}"

        for word in self.search_words:
            header += f"{word[:12]:>15}"

        lines.append(header)
        lines.append("-" * 100)

        for result in self.results:
            row = (
                f"{result['source'][:21]:<22}"
                f"{result['unique_count']:>15}"
            )

            for word in self.search_words:
                row += f"{result['word_counts'].get(word, 0):>15}"

            lines.append(row)

        lines.append("\nWEBSITE LINKS")

        for result in self.results:
            lines.append(
                result["source"] + ": " + result["url"]
            )

        lines.append("\nUNIQUE ALPHABETIC WORDS")

        for result in self.results:
            lines.append("\nWebsite: " + result["source"])
            lines.append(
                "Number of unique words: "
                + str(result["unique_count"])
            )
            lines.append(", ".join(result["unique_words"]))

        return "\n".join(lines)

    def display_results(self):
        """Display the search results."""
        print(self.create_report())

    def save_results(self):
        """Save the results to a text file."""
        if not self.results:
            print("Run a website search before saving.")
            return

        filename = input("Enter results file name: ").strip()

        if not filename:
            print("A file name is required.")
            return

        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(self.create_report())

            print("Results saved to", filename)

        except Exception as error:
            print("Could not save results:", error)


class ShellyL_Vulnerabilities:
    """Downloads and searches CISA vulnerability information."""

    def __init__(self):
        self.vulnerabilities = []

        self.json_url = (
            "https://www.cisa.gov/sites/default/files/feeds/"
            "known_exploited_vulnerabilities.json"
        )

    def get_vulnerabilities(self):
        """Download the CISA vulnerability JSON file."""
        try:
            request = urllib.request.Request(
                self.json_url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

            self.vulnerabilities = data.get(
                "vulnerabilities", []
            )

            with open(
                "CISA_Vulnerabilities.json",
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(data, file, indent=4)

            print("\nCISA data downloaded successfully.")
            print(
                "Number of vulnerabilities:",
                len(self.vulnerabilities)
            )

            return True

        except Exception as error:
            print("Could not get CISA data:", error)
            return False

    def search_vulnerabilities_by_year(self):
        """Search descriptions and group matching CVEs by year."""
        if not self.vulnerabilities:
            print("Download CISA data first.")
            return

        phrase = input(
            "\nEnter a search word or phrase: "
        ).strip().lower()

        if not phrase:
            print("Enter a search word or phrase.")
            return

        yearly_results = {}

        for vulnerability in self.vulnerabilities:
            description = vulnerability.get(
                "shortDescription", ""
            )

            if phrase in description.lower():
                date_added = vulnerability.get("dateAdded", "")
                cve_id = vulnerability.get("cveID", "Unknown")

                if len(date_added) >= 4:
                    year = date_added[:4]

                    if year not in yearly_results:
                        yearly_results[year] = []

                    yearly_results[year].append(cve_id)

        print("\n========== CISA Search Results ==========")
        print("Search phrase:", phrase)
        print(f"\n{'Year':<12}{'Number Found':<18}CVE IDs")
        print("-" * 75)

        if not yearly_results:
            print("No matching vulnerabilities found.")
            return

        for year in sorted(yearly_results):
            cve_ids = ", ".join(yearly_results[year])

            print(
                f"{year:<12}"
                f"{len(yearly_results[year]):<18}"
                f"{cve_ids}"
            )

        print("\nSearch completed.")


class ShellyL_Menu:
    """Displays the program menus."""

    def show_main_menu(self):
        print("\n========== Main Menu ==========")
        print("1. Network Menu")
        print("2. Forensics Menu")
        print("3. Get Web Data Menu")
        print("4. Quit the program")

        return input("Enter choice between 1 and 4: ").strip()

    def show_web_menu(self):
        print("\n======= Get Web Data Menu =======")
        print("1. Get Web HTML Page")
        print("2. Check Vulnerabilities Data")
        print("3. Go Back to Main Menu")

        return input("Enter choice between 1 and 3: ").strip()

    def show_html_menu(self):
        print("\n========== Web HTML Menu ==========")
        print("1. Ask for a URL Interactively")
        print("2. Read URLs From File")
        print("3. Ask for Search Words")
        print("4. Run the Search")
        print("5. Display Results")
        print("6. Save Results to a File")
        print("7. Go Back to Web Data Menu")

        return input("Enter choice between 1 and 7: ").strip()

    def show_vulnerability_menu(self):
        print("\n======= Vulnerabilities Menu =======")
        print("1. Search Vulnerabilities by Year")
        print("2. Go Back to Web Data Menu")

        return input("Enter choice between 1 and 2: ").strip()

    def html_menu(self, web):
        """Control the HTML submenu."""
        while True:
            choice = self.show_html_menu()

            if choice == "1":
                web.ask_for_urls()
            elif choice == "2":
                web.read_urls_from_file()
            elif choice == "3":
                web.ask_for_search_words()
            elif choice == "4":
                web.run_search()
            elif choice == "5":
                web.display_results()
            elif choice == "6":
                web.save_results()
            elif choice == "7":
                break
            else:
                print("Invalid choice. Try again.")

    def vulnerability_menu(self, vulnerabilities):
        """Control the vulnerability submenu."""
        if not vulnerabilities.get_vulnerabilities():
            return

        while True:
            choice = self.show_vulnerability_menu()

            if choice == "1":
                vulnerabilities.search_vulnerabilities_by_year()
            elif choice == "2":
                break
            else:
                print("Invalid choice. Try again.")

    def web_data_menu(self, web, vulnerabilities):
        """Control the Web Data menu."""
        while True:
            choice = self.show_web_menu()

            if choice == "1":
                self.html_menu(web)
            elif choice == "2":
                self.vulnerability_menu(vulnerabilities)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Try again.")

    def main_menu(self, web, vulnerabilities):
        """Run the main menu until the user quits."""
        while True:
            choice = self.show_main_menu()

            if choice == "1":
                print("Network Menu is not included in this version.")
            elif choice == "2":
                print("Forensics Menu is not included in this version.")
            elif choice == "3":
                self.web_data_menu(web, vulnerabilities)
            elif choice == "4":
                print("\nThank you for using the program!")
                break
            else:
                print("Invalid choice. Enter 1, 2, 3, or 4.")


def main():
    menu = ShellyL_Menu()
    web = ShellyL_GetSearchWeb()
    vulnerabilities = ShellyL_Vulnerabilities()

    menu.main_menu(web, vulnerabilities)


if __name__ == "__main__":
    main()
