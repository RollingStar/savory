
name := Savory-0.08
kut := ./kindle_update_tool.py
tar := gnutar

update_files := 001-savory.sh savoryctl
update_files_remove := 001-remove-savory.sh

all: update_$(name)-dx.bin update_$(name)-k2.bin update_$(name)-k2i.bin update_Remove$(name)-dx.bin update_Remove$(name)-k2.bin update_Remove$(name)-k2i.bin

savoryctl: ../scripts/savoryctl
	cp $^ .

update_$(name)-dx.bin: $(update_files)
	$(kut) m -k3 $(name)-dx $^

update_$(name)-k2.bin: $(update_files)
	$(kut) m -k2 $(name)-k2 $^

update_$(name)-k2i.bin: $(update_files)
	$(kut) m -k2iex $(name)-k2i $^

update_Remove$(name)-dx.bin: $(update_files_remove)
	$(kut) m -k3 Remove$(name)-dx $^

update_Remove$(name)-k2.bin: $(update_files_remove)
	$(kut) m -k2 Remove$(name)-k2 $^

update_Remove$(name)-k2i.bin: $(update_files_remove)
	$(kut) m -k2iex Remove$(name)-k2i $^

clean:
	rm -f update_$(name)-{k2,k2i,dx}.bin update_Remove$(name)-{k2,k2i,dx}.bin savoryctl
