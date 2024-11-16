How to create the databse for stockScraper
Make sure mysql is installed via community installer
This step guide is for mac users

Open up terminal and run:
    cd /usr/local/mysql/bin
    ./mysql -u root -p
Enter password for mysql
Execute the following scripts in the command line:
    source /path_to/database_create.sql;
    source /Users/mark/Desktop/Path_to_Millionare/stockScraper/database stuff/database_create.sql;

to resest the database run:
    source /Users/mark/Desktop/Path_to_Millionare/stockScraper/database stuff/reset.sql;
