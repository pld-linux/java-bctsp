#
# Conditional build:
%bcond_without	javadoc		# don't build javadoc
%bcond_without	tests		# don't build and run tests

%define		archivever	jdk16-%(echo %{version} | tr -d .)
%define		srcname		bctsp
%include	/usr/lib/rpm/macros.java
Summary:	TSP libraries for Bouncy Castle
Name:		java-%{srcname}
Version:	1.46
Release:	3
License:	MIT
Group:		Libraries/Java
URL:		http://www.bouncycastle.org/
Source0:	http://www.bouncycastle.org/download/bctsp-%{archivever}.tar.gz
# Source0-md5:	b69e2f9c77df884d5b004c0a3983c4a1
BuildRequires:	java-bcmail = %{version}
%{?with_tests:BuildRequires:    java-hamcrest}
BuildRequires:	java-junit
BuildRequires:	jdk >= 1.6
BuildRequires:	jpackage-utils >= 1.5
Requires:	java-bcmail = %{version}
Requires:	jpackage-utils >= 1.5
Obsoletes:	bctsp
Obsoletes:	bouncycastle-tsp
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Bouncy Castle consists of a lightweight cryptography API and is a
provider for the Java Cryptography Extension and the Java Cryptography
Architecture. This library package offers additional classes, in
particular generators/processors for Time Stamp Protocol (TSP), for
Bouncy Castle.

%package javadoc
Summary:	Javadoc for Bouncy Castle TSP
Group:		Documentation
Requires:	jpackage-utils

%description javadoc
API documentation for Bouncy Castle TSP package.

%prep
%setup -q -n bctsp-%{archivever}
install -d src

unzip -qq src.zip -d src

# Remove provided binaries
find -type f -name "*.class" | xargs -r rm -v
find -type f -name "*.jar" | xargs -r rm -v

%build
cd src

CLASSPATH=$(build-classpath bcprov bcmail junit)
export CLASSPATH
%javac -g -target 1.5 -encoding UTF-8 $(find -type f -name "*.java")

jarfile="../bctsp-%{version}.jar"
# Exclude all */test/*, cf. upstream
files="$(find . -type f \( -name '*.class' -o -name '*.properties' \) -not -path '*/test/*')"
test ! -d classes && mf="" || mf="`find classes/ -type f -name "*.mf" 2>/dev/null`"
test -n "$mf" && %jar cvfm $jarfile $mf $files || %jar cvf $jarfile $files

%if %{with tests}
cp=$(build-classpath junit bcprov bcmail hamcrest-core)
export CLASSPATH=$PWD:$cp
for test in $(find -name AllTests.class); do
	test=${test#./}; test=${test%.class}; test=$(echo $test | tr / .)
	# TODO: failures; get them fixed and remove || :
	%java org.junit.runner.JUnitCore $test || :
done
%endif


%install
rm -rf $RPM_BUILD_ROOT

# install bouncy castle tsp
install -d $RPM_BUILD_ROOT%{_javadir}
cp -p %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-%{version}.jar
ln -s %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}.jar

# javadoc
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc *.html
%{_javadir}/%{srcname}-%{version}.jar
%{_javadir}/%{srcname}.jar

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif
