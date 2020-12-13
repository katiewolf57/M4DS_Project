import matplotlib.pyplot as plt
import pandas as pd 
import re
from datetime import datetime
from datetime import timedelta
import warnings
warnings.filterwarnings("ignore")

# Reading in Data ##
tpc_df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
cfr_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/jhu/COVID-19%20-%20Johns%20Hopkins%20University.csv')


def date_replace(country_info):

    ## creating a list of actual dates, not just numbers
    date_list = []
    ## choosing start date as 2020/01/22 (January, 22nd, 2020) b/c that's when the OWID data starts
    date = datetime(2020, 1, 22)
    for count in country_info["Year"]:
        date_list.append(date)
        date = date + timedelta(days=1)

    ## creating a list of values to replace
    replace_list = []
    for num in country_info["Year"]:
        replace_list.append(num)

    country_info = country_info.replace({"Year":replace_list}, {"Year":date_list})

    return country_info


def get_testing_info(country_name):
	country_info = tpc_df.loc[tpc_df['location'] == country_name]
	cleaned_data = country_info[["date", "tests_per_case"]].copy()

	dates = cleaned_data["date"].tolist()
	datetimes = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
	tests_per_case = cleaned_data["tests_per_case"].tolist()

	return datetimes, tests_per_case

def get_cfr_info(country_name):
    country_info = cfr_df.loc[cfr_df["Country"] == country_name]
    country_info = date_replace(country_info)
    cleaned_data = country_info.iloc[:, [0,1,32]].copy()

    dates = cleaned_data["Year"].tolist()
    datetimes = [pd.Timestamp.to_pydatetime(date) for date in dates]
    cfr = cleaned_data.iloc[:, 2].tolist()

    return datetimes, cfr


testing_tuples = list(zip(get_testing_info("Switzerland")[0], get_testing_info("Switzerland")[1]))
testing_info_df = pd.DataFrame(testing_tuples, columns=["dates", "tests_per_case"])
cfr_tuples = list(zip(get_cfr_info("Switzerland")[0], get_cfr_info("Switzerland")[1]))
cfr_info_df = pd.DataFrame(cfr_tuples, columns=["dates", "cfr"])

tpc_cfr_df = testing_info_df.merge(cfr_info_df, how="inner", on="dates")
tpc_cfr_df = tpc_cfr_df.dropna()



def tpc_cfr_plot(x, y1, y2, country_name):
	months = []
	months.append(x[0])

	for date in x:
		if date.day == 1:
			if date not in months:
				months.append(date)

	fig, ax1 = plt.subplots()
	color = "tab:red"
	ax1.set_xlabel("Date")
	ax1.set_ylabel("Tests Per Case", color=color)
	ax1.plot(x, y1, color=color)
	ax1.tick_params(axis="y", labelcolor=color)


	ax2 = ax1.twinx()

	color = "tab:blue"
	ax2.set_ylabel("Case Fatality Ratio (%)", color=color)
	ax2.plot(x, y2, color=color)
	ax2.tick_params(axis="y", labelcolor=color)

	plt.title("{} Tests Per Case and Case Fatality Ratio (%) with 7 Day Moving Average".format(country_name))

	fig.tight_layout()
	plt.show()

def tpc_cfr_visualization(country_name):
	dates = tpc_cfr_df["dates"].tolist()
	tests_per_case = tpc_cfr_df["tests_per_case"].tolist()
	cfr = tpc_cfr_df["cfr"].tolist()

	tpc_cfr_plot(dates, tests_per_case, cfr, country_name)



tpc_cfr_visualization("Switzerland")

