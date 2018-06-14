JC = javac

CLASSDIR := ../bin

CLASSES := $(addprefix $(CLASSDIR)/,BoardPanel.class GamePage.class)

$(CLASSDIR)/%.class : %.java
	$(JC) -d $(CLASSDIR) $<

all: $(CLASSES)

$(CLASSES): | $(CLASSDIR)

$(CLASSDIR):
	mkdir $(CLASSDIR)
