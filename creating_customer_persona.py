# Creating Customer Personas with Rule-Based Classification


#importing dataset:
import pandas as pd
import math
df = pd.read_csv('./persona.csv')
df.head()

#checking descriptive statistics:
def check_df(dataframe, head=5):
    print("____________________ Shape ____________________")
    print(dataframe.shape)
    print("____________________ Types ____________________")
    print(dataframe.dtypes)
    print("____________________ Head ____________________")
    print(dataframe.head(head))
    print("____________________ NA ____________________")
    print(dataframe.isnull().sum())

check_df(df)

#some analytical calculations:
sales_source=df[["SOURCE", "PRICE"]].groupby("SOURCE").agg({"count"}).T
print(f"Counting of sales by sources:\n{sales_source}")

avg_price_country=df[["COUNTRY", "PRICE"]].groupby("COUNTRY").agg({"mean"})
print(f"Average earnings by countryı:\n{round(avg_price_country,2)}")

total_earn=df[["COUNTRY", "SOURCE","GENDER", "AGE", "PRICE" ]].groupby(["COUNTRY","SOURCE", "GENDER", "AGE"]).agg({"sum"})
print(f"Total earnings by country, source, gender, age:\n{total_earn}")

#sorting by price aggregated query (total_earn)
agg_df=df[["COUNTRY", "SOURCE", "GENDER" , "AGE", "PRICE", ]].groupby(["COUNTRY","SOURCE", "GENDER", "AGE"]).agg("sum").sort_values("PRICE", ascending=False)
agg_df=agg_df.reset_index()
agg_df.head()

#transforming "AGE" to categorical variable with statistical methods
Xmax=agg_df["AGE"].max()  #66
Xmin= agg_df["AGE"].min() #15
N=agg_df["AGE"].count() #348

k=1 + (3.3 *math.log10(N))  #number of categories  (first and last categories was combined due to low frequency)
i=(Xmax-Xmin)/k  # interval of categories

agg_df["AGE_CATEGORY"]=pd.cut(agg_df["AGE"], bins = [0, 22, 29, 36, 43, 50, 57 , Xmax],
                      labels=["0-21", "22_28", "29_35", "36_42", "43_49", "50_56", "57+"])

agg_df["CUSTOMER_LEVEL"] =agg_df.loc[:,[col for col in agg_df.columns if agg_df[col].dtypes != "int64"]].T.apply(lambda x: "_".join(x).upper())

"""
Examples of CUSTOMER_LEVEL column:
"country"_"source"_"gender"_"age_category"
USA_ANDROID_MALE_0-21 
DEU_IOS_FEMALE_29_35  
"""

#creating new dataframe with "CUSTOMER_LEVEL" and "PRICE"
agg_df2=agg_df[["CUSTOMER_LEVEL", "PRICE"]]
agg_df2.head()

#"CUSTOMER_LEVEL" is not unique
agg_df2.CUSTOMER_LEVEL.value_counts()

#calculating average of "PRICE" each "CUSTOMER_LEVEL"
agg_df2 = agg_df2.groupby("CUSTOMER_LEVEL").agg({"PRICE":"mean"})
agg_df2.reset_index(inplace=True)
agg_df2.head()

#Segmenting personas by "PRICE" column with qcut function
agg_df2["SEGMENT"]=pd.qcut(agg_df2["PRICE"], 4, labels=["D", "C", "B", "A"])
agg_df2.head()

#Average earnings by segments
agg_df2.groupby("SEGMENT").agg({"PRICE":"mean"}).sort_values("PRICE",ascending=False)

#Classifying new customers by segments
def search_new_cust(dataframe, country_code, source_code, gender_code, age_cat):
    country = dataframe["CUSTOMER_LEVEL"].str.contains(country_code)
    source = dataframe["CUSTOMER_LEVEL"].str.contains(source_code)
    gender = dataframe["CUSTOMER_LEVEL"].str.contains(gender_code)
    age = dataframe["CUSTOMER_LEVEL"].str.contains(age_cat)
    print(dataframe[country&source&gender&age])

#New customer: 25 years old, ANDROID user, a Turkish woman.
search_new_cust(agg_df2,"TUR","ANDROID","FEMALE", "22_28")
# Segment of new customer is A.

#New customer: 52 years old, IOS user, a French man.
search_new_cust(agg_df2,"FRA", "IOS", "MALE", "50_56")
#Segment of new customer is D.
