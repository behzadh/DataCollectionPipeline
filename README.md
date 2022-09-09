# Data Collection Pipeline

> The idea of this project is to collect data from any website and build pipelines to store data locally and/or on the cloud.

### Web Scraping

> Web scraping is the act to use a program to grab and download data from the Web.

- There are several modules in Python to scrape data from web pages such as:
    - Webbrowser: Opens a page in a browser
    - Requests: Downloads files and web pages from the Internet.
    - Beautiful Soup: Parses HTML.
    - Selenium: Launches and controls a web browser.

- For this project -> all the above modules have been tested in the 'test_scrappers.py' file.

- For scrapping data from the Ikea website -> the Selenium method is been used. Please check 'utils/ikea.py' for more details.

### Retrieve data from a page

> For this milestone -> we use the Selenium module and XPath expressions to select the details and extract them from the web pages.

- These could be done by creating different methods to get a text or images from a website. For example:

```python
    def _download_image(self -> img_name: str -> dir_name: str = '_' -> download: bool = True):
        '''
        This function is used to download the main image for each product and save it to the 'images' folder

        Parameters
        ----------
        img_name (str)
            Defines the name of the image
        dir_name (str)
            Gives the image name a spesific id (like production id or unique id) as well as creating a parent directory named dir_name for the 'images' folder  
        download (bool)
            If True -> downloads the image. Otherwise -> just get the src link of the image

        Returens
        --------
        list
            the src link of the image
        '''
        src = self.driver.find_element_by_xpath('//div[@class="pip-product__left-top"]//img[@class="pip-aspect-ratio-image__image"]').get_attribute('src') # Prepares the image source to download
        if download == True:
            if not os.path.exists(f'raw_data/{dir_name}/images'): os.makedirs(f'raw_data/{dir_name}/images') # Creats 'raw_data -> {id} and images' folders if it is not exist
            sleep(1)
            try:
                urllib.request.urlretrieve(src -> f"./raw_data/{dir_name}/images/{img_name}_{dir_name}.jpg") # saves images to the folder
            except:
                print(f"Couldn't download the main image: {src} for {dir_name} product")
        return src
```
This method which is a private method will first create folders and subfolders and then downloads an image if applicable.

- Unique ID (UID): Usually -> each product or element has a unique string to represent that product in a webpage. This ID must be deterministic -> as it can be used to prevent re-scraping the same product data later on.

- Universally Unique ID (UUID): Along with the UID -> it is typical to reference each record with a universally unique ID (UUID). It's a 128-bit label used for information in computer systems. They can be generated with the python UUID package.

```python
    def generate_uuid(self) -> str:
        '''
        This method will generates Universal Unique IDs. 
        
        UUID is a unique 128-bit label used for information in computer systems. It looks like a 
        32-character sequence of letters and numbers separated by dashes.
        ex: 354d86ec-d243-4a97-9b09-f833d9c7ebfa

        Returns
        -------
        str
            A singal UUID
        '''
        return str(uuid.uuid4())
```
UUID looks like a 32-character sequence of letters and numbers separated by dashes. For example:

```code
354d86ec-d243-4a97-9b09-f833d9c7ebfa
```
- Once we have the access to all information in a webpage we need to store them. One option is to store info in a dictionary and save it locally. For the Ikea project a dictionary is defiened to record Product_id -> UUID_number -> Price -> Name -> Description -> Image_link -> Image_all_links in a dictionary and store it for each product localy as a json file called 'data.json'.

### Testing the code functionality

> In this section we review the functionality of our code by testing each part of our code sparately. Testing is a thorough and formal process for applications that must not fail. 

- We have used unittest package to test our code. Unittest is a Python package testing framework and it can be also used for integration testing. We have used its assertions method to check the behaviour of our code. It also includes the tool for running tests.

- For this project a test class is prepared in the 'test_ikea.py' which can be find in the 'test_files' folder.

- This class has three main parts:
    - Setup: which is a methid to setup the testing process.
    ```python
    def setUp(self) -> None:
        self.scraper_obj = DataCollection(url="https://www.ikea.com/gb/en/")
        return super().setUp()
    ```
    - test_methods from the main code (ikea.py) -> for example:
    ```python
    def test_download_multiple_images_false(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_false = self.scraper_obj._download_multiple_images("image_name" -> "check_directory" -> download=False)
        self.assertEqual(len(test_download_false) -> 8)
        self.assertEqual(test_download_false[0] -> "https://www.ikea.com/gb/en/images/products/micke-desk-oak-effect__0515989_pe640126_s5.jpg?f=s")
        self.assertFalse(os.path.exists('raw_data/check_directory'))

    def test_download_multiple_images_true(self):
        self.scraper_obj.driver.get("https://www.ikea.com/gb/en/p/micke-desk-oak-effect-20351742/")
        test_download_true = self.scraper_obj._download_multiple_images("image_name" -> "check_directory" -> download=True)
        self.assertEqual(len(test_download_true) -> 8)
        self.assertEqual(test_download_true[0] -> "https://www.ikea.com/gb/en/images/products/micke-desk-oak-effect__0515989_pe640126_s5.jpg?f=s")
        self.assertTrue(os.path.exists('raw_data/check_directory'))    
    ```
    to check if the '_download_multiple_images' methid works correctly in both true-false situations.

    - Tearing down method to close the testing:
    ```python
    def tearDown(self) -> None:
        self.scraper_obj.driver.quit()
        return super().tearDown()
    ```

you can run the testing by the folowing command from the root directory:
```code
python test_code.py 
```

### Scalably storing data

> In the digital world -> everything we interact with and work on -> creates data. All the files -> images -> audio/video data that we daily watch and use generates an increasing quantity of data. This data needs to be stored somewhere to be able to access and analyze it later. Storing data is one of the crusial tasks in each project or orgnization. In this section we review different methods to store data.

- Storing data can be prepared in two ways:
    1. Locally: on a PC or a hard drive
    2. On cloud: like Amazon -> Google and MicroSoft cloud platforms

1. Store data locally: 
    - This can be done by leting the code to create a directory on a local system like a PC or a hard drive and store differen types of data locally. The most comon files to store data are json -> csv and images.
    ```python
    def store_raw_data_locally(self -> dict: dict -> dir_name: str = '_'):
        print('Storing data locally...')
        if not os.path.exists(f'~/{dir_name}'): os.makedirs(f'~/{dir_name}') 
        with open(f'~/{dir_name}/data.json' -> 'w') as fp:
            json.dump(dict -> fp)
    ```
    This function will first create a directory with 'dir_name' if it is not exsist. Then -> stores data (here a dictionary) to a json file -> 'data.json'.

2. Store data on cloud:
    - What are the benefits of cloud storage:
        - Total Cost of Ownership
        - Time to Deployment
        - Performance
        - Reliability and Security
    
    - As mentioned earlier there are different platforms to store data on cloud. However -> here we only focus on two Amazon Web Service (AWS) storage service.
        1. Amazon S3 (Amazon Simple Storage Service)
        2. AWS Relational Database Service (RDS)

    1. Amazon S3 buckets are data lakes where you can store your files. In order to access S3 buckets you need to do the following steps:
        - Create an IAM user on the Amazon website.
        - Download and configure AWS CLI
        ```code 
        pip install awscli
        aws configure
        ```
        - Using boto3 for using your AWS resources from Python
            - boto3 is a library that allows us to work with AWS from our python script. 
            ```python
            import boto3 
            s3_client = boto3.client('s3')
            # response = s3_client.upload_file(file_name -> bucket -> object_name)
            response = s3_client.upload_file('cat_0.jpg' -> 'cat-scraper' -> 'cat.jpg')
            ```
            This a simple example to upload a file on Amazon S3 bucket by using boto3 library. file_name is the directory of the file you want to upload -> bucket is the name of your S3 bucket -> and object_name is the name you want to give to your file once uploaded.
            We can also see the content of a bucket and then download the files:
            ```python
            import boto3
            s3 = boto3.resource('s3')
            my_bucket = s3.Bucket('datacollectionprojectbucket')

            for file in my_bucket.objects.all():
                print(file.key)

            s3 = boto3.client('s3')
            s3.download_file('datacollectionprojectbucket' -> 'raw_data/S79429602/data.json' -> 'my.json')
            ```
    
    2. AWS Relational Database Service -> RDS -> is a service for hosting databases on the AWS cloud. AWS RDS allows you to create a database in the cloud. It is a highly scalable database that can be used for a variety of purposes. Let's create a PostgreSQL database.
        - Go to the AWS Console and select the Services tab. 
        - Click on the RDS tab. 
        - After that -> click on 'Create database'
        - Select PostgreSQL as the type of database and setup the database
        - Click on Create -> and wait for it to be created.
        - Now we are ready to connect to the database as following! The default user and database are postgres and postgres.
        ```python
        from sqlalchemy import create_engine
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.c8k7he1p0ynz.us-east-1.rds.amazonaws.com' # Change it for your AWS endpoint
        USER = 'postgres'
        PASSWORD = 'Cosamona94'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        print(engine.connect()) # Check if everything works
        ```
        - In this step we can store our data in a table on the RDS dabase:
        ```python
        def rds_tables_with_sqlalchemy(self -> df_name: pd.DataFrame -> table_name: str = 'table_name'):
            '''
            This functions stores data as a table on the AWS RDS

            Parameters
            ----------
            df_name (DataFrame)
                It's the data frame that will be store as a table on the RDS
            table_name (DataFrame)
                It's the name of created table on the RDS
            ''' 
            print('Storing data on RDS...')
            df_name.to_sql(table_name -> self.engine -> if_exists='replace')
        ```
        - NOTE: Unfortunately -> AWS RDS doesn't allow see the tables you created -> but to can still access to them using pgAdmin or SQLAlchemy itself.

        - In order to remove a table from RDS you can run the following command on pgadmine4:
        ```code 
        drop table if exists "rds-test";
        ```
        
### Make a Docker container and run a Docker image on the AWS EC2

> Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers. The service has both free and premium tiers. In this section -> we review all steps to create a Docker image and run it locally as well as pushing the image to DockerHub. Then -> will explain how to pull this image from DockerHub and run it on an EC2 instance.

- Create a Docker image:
    - In order to create a Docker image -> first make sure your code is running without any erros.
    - Install 'Docker' on your machine.
    - Create a 'Dockerfile' to build your project image locally. Docker file is responsible for creating our image and pre-install all requirments and copy the project to the image.
    ```dockerfile
    FROM python:3.7 

    RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
        && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
        && apt-get -y update \
        && apt-get install -y google-chrome-stable \
        && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
        && apt-get install -yqq unzip \
        && apt-get install nano \
        && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

    WORKDIR /workdir
    VOLUME ["/workdir"]

    COPY . .

    RUN pip install -e .

    CMD ["python" -> "main.py"]
    ```
    First line will let us to load the language that we want to run our code and can call a specific version. It is Python 3.7 in this example. Then pre install the necessary packages related to our project. In this case 'google-chrome-stable' and 'nano' for example. WORKDIR is the mkdir in Docker and VOLLUME is cd.
    Then we can copy the whole project to the image and install the dependencies to our code. Once these done -> we need to call a command 'CMD' to tell how we want to execute our project when we call 'docker run'.
    - If your project is using selenium to scrap data from Chrome or Firefox you can use the following files:
        - Google Chrome:
        ```code
        These are the steps you have to follow to create the Dockerfile. For each of the steps -> you have to figure out what Dockerfile instructions you have to use for each step
        1. Pull a Python image. For example -> python:3.8 will do the job
        2. Adding trusting keys to apt for repositories -> you can download and add them using the following command:
        `wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -`
        3. Add Google Chrome. Use the following command for that
        `sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'`
        4. Update apt:
        `apt-get -y update`
        5. And install google chrome:
        `apt-get install -y google-chrome-stable`
        6. Now you need to download chromedriver. First you are going to download the zipfile containing the latest chromedriver release:
        ```
        wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
        ```
        7. You downloaded the zip file -> so you need to unzip it:
        ```
        apt-get install -yqq unzip
        unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
        ```
        8. Copy your application in a Docker image
        9. Install your requirements
        10. Run your application
        ```
        - Firefox:
        ```
        FROM python:3.9

        # Update the system and install firefox
        RUN apt-get update 
        RUN apt -y upgrade 
        RUN apt-get install -y firefox-esr

        # get the latest release version of firefox 
        RUN latest_release=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest \
            | grep tag_name | sed -E 's/.*"([^"]+)".*/\1/') && \
            # Download the latest release of geckodriver
            wget https://github.com/mozilla/geckodriver/releases/download/$latest_release/geckodriver-$latest_release-linux32.tar.gz \
            # extract the geckodriver
            && tar -xvzf geckodriver* \
            # add executable permissions to the driver
            && chmod +x geckodriver \
            # Move gecko driver in the system path
            && mv geckodriver /usr/local/bin

        COPY . . 

        RUN pip install -r requirements.txt

        CMD ["python" -> "test.py"]
        ```
    - To build the docker image -> run the following command:
    ```
    docker build -t user_dockerhub/image_name .
    ```
    It is better to put your docerhub user in front of your image in case you want to push your image to DockerHub but it's not required.
    - Now you can run your image by:
    ```code
    docker run -it user_dockerhub/image_name
    ```
    - Usefull Docker commands:
        1. to see the docker images: 
        ```code
        docker image ls
        ```
        2. to see the docker containers: 
        ```code
        docker ps -aq
        ```
        3. to remove the docker container(s): 
        ```code
        docker rm -f container_id
        ```
        or to delete all containers:
        ```
        docker rm -vf $(docker ps -aq)
        ```
        4. to remove the docker image(s): 
        ```code
        docker rmi -f image_id
        ```
        or to delete all images:
        ```
        docker rmi -f $(docker images -aq)
        ```
        5. to check the codes inside an image:
        ```code
        docker run -it user_dockerhub/image_name bash
        ```
- Push the image to the DockerHub:
    - First login to your accaount:
    ```code
    docker login
    ```
    - Create a repository with the same name as your image: user_dockerhub/image_name
    - Run this command:
    ```code
    docker push user_dockerhub/image_name
    ```
- Pull the image from DockerHub:
``` code
docker pull user_dockerhub/image_name
```
- Create an EC2 instance:
    Navigate to the AWS dashboard and sign up an new EC2 instance to deploy your project.
    1. Select a region. 
    2. Navigate to the EC2 Console. 
    3. Create the EC2 instance. 
    4. Choose an instance type. We use ubuntu for this project.
    5. Configure storage. 
    6. Tag the instance. 
    7. Build in security. 
    8. Enable SSH access with a key.

- Now we can access to our EC2 instance by an SSH connection:
```code 
ssh -i "your_ec2_key.pem" ubuntu@ec2_ip_.compute-1.amazonaws.com 
```
- We are ready to pull our docker image here and run our project from here.
- In order to store data from the docker image we can mount a volume on EC2 and connect it to our image:
    1. create a folder on your EC2: 
    ```code 
    sudo mkdir raw_data
    ```
    2. mount this volume to your image work directory:
    ```code
    sudo docker run  -v /home/ubuntu/raw_data:/workdir/raw_data -it user_dockerhub/image_name
    ```

### Monitoring and Alerting

> In each project it is essential to monitor the software and the hardware once the code running. Prometheus and Grafana are excellent tools to implement event monitoring and alerting to refine your systems. In this section we review these tools

- Prometheus:
    - Prometheus is an open-source software that collects metrics from targets by "scraping" metrics HTTP endpoints.
    - All prometheus data is stored as timestamped timeseries differentiated by metric and (optionally) label. For instance process_cpu_seconds_total which will calculate the total cpu usage of our Prometheus instance will be displayed as:
    ```code
    process_cpu_seconds_total{instance="localhost:9090" -> job="prometheus"}
    ```
    - Installation: There are two methods to install prometheus:
        1. Go to their [download page](https://prometheus.io/download/) and download the specific version of Prometheus for your operating system.
        2. run prometheus inside Docker container
            - First pull the Prometheus Docker image from Docker
            ```code
            docker pull prom/prometheus
            ```
            - create a prometheus.yml file which is a config file for prometheus. For example:
            ```code
            global:
                scrape_interval: 15s # By default -> scrape targets every 15 seconds.
                # Attach these labels to any time series or alerts when communicating with
                # external systems (federation -> remote storage -> Alertmanager).
                external_labels:
                    monitor: 'codelab-monitor'

            # A scrape configuration containing exactly one endpoint to scrape:
            # Here it's Prometheus itself.
            scrape_configs:
                # The job name added as a label `job=<job_name>` to any timeseries scraped
                - job_name: 'prometheus'
                    # Override the global default and scrape targets from job every 5 seconds.
                    scrape_interval: '5s'
                    static_configs:
                    - targets: ['localhost:9090']
            ```
            - We can then build the image using the following command -> you will just need to change the /path/to/prometheus.yml/ path to the directory path your prometheus.yml config file is stored in locally (remember to watch out for file paths with spaces!).
            ```code
            sudo docker run --rm -d \
                --network=host \
                --name prometheus\
                -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
                prom/prometheus \
                --config.file=/etc/prometheus/prometheus.yml \
                --web.enable-lifecycle 
            ```
            the --web.enable-lifecycle flag is for enabling of reloading the config from the command line.
            - Prometheus will now be running so we can simply go to localhost:9090 in your browser.
            - A nice thing about Prometheus is it reloads it's configuration based on the config file automatically or you can change it live or even force it to reload by using the /-/reload flag. That can be done by 
            ```code
            curl -X POST http://localhost:9090/-/reload
            ```
            - Node exporter (Linux/MAC): Node exporter is a single static binary one can download and run straight from the workstation.
                - Following command will download the exporter -> unpack the .tar.gz archive (we assume you have Linux based system!).
                - If on MacOS -> run 
                ```code 
                brew install node_exporter
                ```
                - Once install you can run it from your terminal as
                ```code
                node exporter
                ```
            - Configuring Prometheus to track Docker:
                - We need edit Dockers configuration by editing the daemon.json docker file or by editing Docker Desktops configuration file.
                    - For Linux: Navigate to /etc/docker/daemon.json -> if the file doesn't already exist then create it. sudo touch daemon.json.
                    - For MAC/Windows: Go to Docker Desktop -> click the cog to go to settings > Docker Engine.
                - Add this code to configure scraping of metrics either the daemon.json file or to the Docker Engine config. Add the code the the section of the .json file where you see the experimental key value already there.
                ```code
                {
                    "metrics-addr" : "127.0.0.1:9323" ->
                    "experimental": true ->
                    "features": {
                    "buildkit": true
                    }
                }
                ```
                - update your Prometheus.yml to add docker as a target so Prometheus can begin scraping the metrics. Add docker as a target in your Prometheus.yml:
                ```code
                global:
                scrape_interval: '15s'  # By default -> scrape targets every 15 seconds.
                scrape_timeout: '10s'
                external_labels:
                    monitor: 'codelab-monitor'

                scrape_configs:

                # Prometheus monitoring itself
                - job_name: 'prometheus'
                    scrape_interval: '10s'
                    static_configs:
                    - targets: ['localhost:9090']

                # OS monitoring
                - job_name: 'wmiexporter'
                    scrape_interval: '30s'
                    static_configs:
                    - targets: ['localhost:9182']

                # Docker monitoring
                - job_name: 'docker'
                        # metrics_path defaults to '/metrics'
                        # scheme defaults to 'http'.
                    static_configs:
                    - targets: ['127.0.0.1:9323'] # metrics address from our daemon.json file
                ```
    - Note: One can repeat the same process to run Prometheus on an EC2 instance. 
        - If you are going to run additional commands on the EC2 instance -> you will need to run the container in the background by adding -d to the docker command.
        - Prometheus should be available to view metrics on port 9090 on your EC2 instance.
        - You will need to configure your EC2 security group to allow access to this port.
            - Go to EC2 instance -> Security -> Security groups
            - For Inbound rules:
                - Add a 'custom TPC' with port 9090
                - Add an 'SSH' rule with port 22 and select 'My IP' for source ifo
            - For Outbound rules:
                - Add an 'HTTP' rule with port 80 and select 'My IP' for source ifo
        - You can then view Prometheus from <IP address of the EC2 instance>:9090.

- Grafana:
    - Grafana is an enterprise level solution designed to allow you to query -> visualise -> alert on and understand your data no matter where it's stored. Grafana does this through the ability to create custom dashboards for almost any service so you can monitor and observe all critical infomartion in one centralised location.
    - Please see the Grafana homepage [here](https://grafana.com/grafana/) for more information.
    - Installation:
        - Please go to the [Grafana download page](https://grafana.com/grafana/download) and follow the instructions to install it. 
        - Grafana will then be configured as a service or server on your system. 
        - You can then access the Grafana login page from localhost:3000. 
        - Note: Initially you will login using admin as the username and admin as the password -> Grafana will then ask you to configure a new admin password before logging in.
    - Adding Prometheus as a data source:
        - Grafana comes with the ability to add many predefined data sources easily and each has their own Query editor which is individually customised to work with each data source.
        - You can get a full list of data sources and more information on each [here](https://grafana.com/docs/grafana/latest/datasources/).
        - To allow Grafana to start tracking your metrics on a dashboard please try the following steps:
            - Click the cog on the left hand navigation panel in Grafana and click 'data sources' this is where you will be able to add your data sources to output to Grafana.
            - Search for Prometheus using the search box
            - Select Prometheus to be taken to the configuration page
            - In the URL field we have configured it to be host.docker.internal:9090 since we are running Prometheus in a Docker container.
            - Leave all other settings as defaults then click Save & test to test the connection to Prometheus
            - You can learn more about adding data source at the following [link](https://grafana.com/docs/grafana/latest/datasources/add-a-data-source/).
    - Creating a dashboard:
        - Now that we have Prometheus added as a data source we can now create a dashboard to track some Prometheus metrics:
            - Click the plus icon on the navigation bar of Grafana then Create to begin creating a new one. You will be given three options:
                1. Add an empty panel: Allows you to add a panel to track metrics or logs.
                2. Add a new row: Add a row which you can add panels to to separate them by case i.e you can have a row to alert you of CPU usage and row to alert of RAM usage.
                3. Add a panel from the panel library: When creating panels you can optionally save them in a panel library which will allow you to quickly recreate the panel on another dashboard.
            Read more about library panels [here](https://grafana.com/docs/grafana/v9.0/dashboards/manage-library-panels/).
            - One can create multiple different kinds of panels with different queries and -> orgainise dashboard by using rows so that it is layed out appropriately.
    - Note: One can create a 'data source' for an Amazon EC2 instance on Grafana by adding <IP address of the EC2 instance>:9090.

### Set up a CI ->CD pipeline and GitHub actions

> GitHub Actions allow us to automate various stages of software development if one uses GitHub

- Key characteristics of GitHub actions are:
    - event driven - if something happens inside our GitHub repository (e.g. pull request) we can run automated piece of code
    - configuration-oriented - we use .yaml to configure necessary workflows
    - customizable - we can create our own specific GitHub Action with docker or JavaScript
    - allows simple Continuous Integration (CI) - each Pull Request/Merge can be automatically tested
    - allows simple Continuous Deployment/Delivery (CD) - after our tests passed we can create a pipeline which automatically deploys our code for others to use

- GitHub Actions Concepts:
    - Key concepts in GitHub Actions one should understand are:
        - Events - anything that happens inside the repository like new issue -> pull request -> merging etc. 
        - Workflow - automated procedure added to the repository. Workflows consist of...
        - Jobs - set of steps running on the same machine
        - Step - individual task which can run action/shell commands on the machine
        - Action - standalone commands set up individually in separate/the same GitHub repository
        - Runner - server with [Github Actions runner](https://github.com/marketplace/actions/github-action-for-latex) installed.
    - Things to keep in mind:
        - Full list of events triggering workflows
        - Jobs in a workflow run in parallel by default
        - We can create dependencies between jobs (for example deployment relies on testing job passing correctly)
        - We can use any action set up publicly (for example: create LaTeX documents with actions)
        - Runners are provided by GitHub for free (see limits in different tiers [here](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration))
        - We can also setup our own runners

- Create a GitHub Action:
    1. Create a folder in our repository containing workflows
    ```code
    mkdir /.github/workflows
    ```
    2. In workflows folder create a .yml file (ex: main.yml)
    3. Define GitHabu Action jobs inside the main.yml
    ```code
    name: CI
    # Controls when the workflow will run
    on:
    # Triggers the workflow on push or pull request events but only for the "main" branch
    push:
        branches: 
        - "main" 
    pull_request:
        branches: 
        - "main" 

    # Allows you to run this workflow manually from the Actions tab
    workflow_dispatch:

    # A workflow run is made up of one or more jobs that can run sequentially or in parallel
    jobs:
    # This workflow contains a single job called "build"
    build_docker_image:
        # The type of runner that the job will run on
        runs-on: ubuntu-latest

        # Steps represent a sequence of tasks that will be executed as part of the job
        steps:
        -
            name: Checkout 
            uses: actions/checkout@v2
        -
            name: Login to Docker Hub
            uses: docker/login-action@v1
            with:
            username: ${{ secrets.DOCKER_HUB_USERNAME }}
            password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
    ```
    This Yaml file will login to your DockerHub using your GitHub secrets for your DockerHub user name and passwords. Please see [this video](https://www.youtube.com/watch?v=CDWLWjnYSGg&ab_channel=MicrosoftDevRadio) explaining how to set up your GitHub secrets.

### Cronjobs

> On the EC2 instance -> a cronjob is been created to restart the scraper every day.

- In order to set a cronjob:
    - run the following command:
    ```code
    crontab -e
    ```
    - Choose an editor to edit the file.
    - Edit the time to run you command. Please check [here](https://crontab.guru/) to check how you can set up a time.
    - Save the file and exit
For more details please watch [this video](https://www.youtube.com/watch?v=VztRqRXeyn0&ab_channel=JohnWatsonRooney).

### How to run the Data Collection Pipline project

1. Clone the Data Collection Pipline to your work place
```code
git clone https://github.com/behzadh/DataCollectionPipeline.git
```
2. Update the config_file with your keys for Amazon S3 and RDS
```code
[KEY]
# S3 keys
AWSAccessKeyId=
AWSSecretKey=
AWSBucketName=

# RDS keys
DATABASE_TYPE=
DBAPI=
ENDPOINT= 
USER='postges'
PASSWORD=
PORT=5432
DATABASE=postgres
```
3. Run the following command inside the 'DataCollectionPipeline' directory.
```code
python main.py --local --folder raw_data --s3 --rds --tab test_new --img --word desk
```
- The Arguments are as following and they are optional:
```
'--local'-> To Store data locally
'--s3'-> To Store data on AWS S3
'--rds'-> To Store data on RDS
'--imgs'-> To Store images
'--folder' -> Folder\'s name to store data (ex: raw_data)
'--word' -> A word to be typed in search bar (ex: desk)
'--table' -> user rds table (ex: table_name)
```
4. To run tests for testing the code's methods:
```code
python test_code.py
```