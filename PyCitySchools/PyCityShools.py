import pandas as pd
import os

# Check out this nifty thing. I pass the data frame through this later to format the whole thing
def formatData(data):
    try:
        return f"{data:,.2f}"
    except:
        ValueError
        return(data)
    
# I had a problem with my computer not recongnizing the files location as the current working directory.
# This helped me resolve it by forcing the computer to do my bidding.
currentDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentDir)

# Get the resource files
schoolDataPath = os.path.join("Resources", "schools_complete.csv")
studentDataPath = os.path.join("Resources", "students_complete.csv")
schoolData = pd.read_csv(schoolDataPath)
studentData = pd.read_csv(studentDataPath)

# Collect and mathatize all the data for the district summary dataframe
schoolNames = schoolData['school_name'].unique()
numStudents = schoolData['size'].sum()
districtPassingMath = (studentData['math_score'] >= 70).sum() / numStudents * 100
districtPassingReading = (studentData['reading_score'] >= 70).sum() / numStudents * 100
districtOverallPassing = ((studentData['math_score'] >= 70) & (studentData['reading_score'] >= 70)).sum() / numStudents * 100

# Create the dataframe for the district summary, and format the data.
districtSummary = pd.DataFrame({
    "District Wide": [len(schoolNames),                                 # Number of schools
    '{:,}'.format(numStudents),                                         # Number of students
    '${:,}'.format(schoolData['budget'].sum()),                         # Total budget
    '{:.2f}'.format(studentData['math_score'].mean()),                  # Average math score
    '{:.2f}'.format(studentData['reading_score'].mean()),               # Average reading score
    '{:.2f}%'.format(districtPassingMath),                              # Percent passing math
    '{:.2f}%'.format(districtPassingReading),                           # Percent passing reading
    '{:.2f}%'.format(districtOverallPassing)                            # Percent overall passing
    ]},index = pd.Index(["Number of Schools", "Total Students", "Total Budget", "Average Math Score",
        "Average Reading Score", "% Passing Math", "% Passing Reading", "% Overall Passing"]))

# Collect and mathatize the data for the school summary dataframe
groupedSchoolData = studentData.groupby("school_name", sort = False)
averagePassingMath = groupedSchoolData['math_score'].mean().values
averagePassingReading = groupedSchoolData['reading_score'].mean().values
passingMath = (groupedSchoolData['math_score'].apply(lambda x: (x >= 70).sum())) / schoolData['size'].values * 100
passingReading = (groupedSchoolData['reading_score'].apply(lambda x: (x >= 70).sum())) / schoolData['size'].values * 100
studentData["pass both"] = (studentData["math_score"] >= 70) & (studentData["reading_score"] >= 70)
overallPassing = groupedSchoolData["pass both"].mean() * 100
spendingBins = [0, 585, 630, 645, 680]
spendingLabels = ["<$585", "$585-630", "$630-645", "$645-680"]
sizeBins = [0, 1000, 2000, 5000]
sizeLabels = ["Small (<1000)", "Medium (1000-2000)", "Large (2000-5000)"]

# Create a dataframe for the school summary and format the data.
schoolSummary = pd.DataFrame({
    "School Name": schoolNames,
    "School Type": schoolData["type"],
    "Total Students": schoolData['size'],
    "Total School Budget": schoolData['budget'],
    "Per Student Budget": (schoolData['budget'] / schoolData['size']),
    "Average Math Score": averagePassingMath,
    "Average Reading Score": averagePassingReading,
    "% Passing Math": passingMath.values,
    "% Passing Reading": passingReading.values,
    "% Overall Passing": overallPassing.values,
    "Spending Ranges (Per Student)": pd.cut(schoolData['budget'] / schoolData['size'],
                                            bins = spendingBins, labels =spendingLabels),
    "School Size":pd.cut(schoolData['size'], bins = sizeBins, labels= sizeLabels) 
    })

# Create a dataframe for the summary of grades based on school spending
schoolGroupedSpending = schoolSummary.groupby("Spending Ranges (Per Student)", sort = False)
spendingSummary = pd.DataFrame({
    "Average Math Score": schoolGroupedSpending['Average Math Score'].mean(),
    "Average Reading Score": schoolGroupedSpending['Average Reading Score'].mean(),
    "% Passing Math": schoolGroupedSpending['% Passing Math'].mean(),
    "% Passing Reading": schoolGroupedSpending['% Passing Reading'].mean(),
    "% Overall Passing": schoolGroupedSpending['% Overall Passing'].mean()
})
spendingSummary = spendingSummary.applymap(formatData)

#  Create a dataframe for the summary of grades based on school size
schoolGroupedSize = schoolSummary.groupby("School Size", sort = False)
sizeSummary = pd.DataFrame({
    "Average Math Score": schoolGroupedSize['Average Math Score'].mean(),
    "Average Reading Score": schoolGroupedSize['Average Reading Score'].mean(),
    "% Passing Math": schoolGroupedSize['% Passing Math'].mean(),
    "% Passing Reading": schoolGroupedSize['% Passing Reading'].mean(),
    "% Overall Passing": schoolGroupedSize['% Overall Passing'].mean()
})
sizeSummary = sizeSummary.applymap(formatData)

# Create a dataframe for the summary of grades based on school type
schoolGroupedType = schoolSummary.groupby("School Type", sort = False)
typeSummary = pd.DataFrame({
    "Average Math Score": schoolGroupedType['Average Math Score'].mean(),
    "Average Reading Score": schoolGroupedType['Average Reading Score'].mean(),
    "% Passing Math": schoolGroupedType['% Passing Math'].mean(),
    "% Passing Reading": schoolGroupedType['% Passing Reading'].mean(),
    "% Overall Passing": schoolGroupedType['% Overall Passing'].mean()
})
typeSummary = typeSummary.applymap(formatData)
schoolSummary = schoolSummary.applymap(formatData)

# Sort the school summary by school name, then highest and lowest performing.
schoolSummary.sort_values('School Name', inplace = True)
highestPerformingSchools = schoolSummary.sort_values('% Overall Passing', ascending = False)
lowestPerformingSchools = schoolSummary.sort_values('% Overall Passing')

# Make a pivot table for math scores by grade and format it to look all nice and stuff
mathScoresByGrade = pd.pivot_table(studentData, index='school_name', columns='grade',
                                   values='math_score', aggfunc='mean')
mathScoresByGrade = mathScoresByGrade.reindex(columns = ['9th', '10th', '11th', '12th'])

# Do all the same stuff here but for reading
readingScoresByGrade = pd.pivot_table(studentData, index='school_name', columns='grade',
                                      values='reading_score', aggfunc='mean')
readingScoresByGrade = readingScoresByGrade.reindex(columns = ['9th', '10th', '11th', '12th'])

districtSummary = districtSummary.to_string()
schoolSummary = schoolSummary.to_string()
highestPerformingSchools = highestPerformingSchools.to_string()
lowestPerformingSchools = lowestPerformingSchools.to_string()
spendingSummary = spendingSummary.to_string()
sizeSummary = sizeSummary.to_string()
typeSummary = typeSummary.to_string()

print(districtSummary)
print(schoolSummary)
print(highestPerformingSchools)
print(lowestPerformingSchools)
print(spendingSummary)
print(sizeSummary)
print(typeSummary)
print(mathScoresByGrade)
print(readingScoresByGrade)